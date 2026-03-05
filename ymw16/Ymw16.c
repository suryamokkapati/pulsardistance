#define _GNU_SOURCE


#include <math.h>
#include <stdio.h>
#include "ymw16.h"


#define D2R   (M_PI / 180.0)
#define R2D   (180.0 / M_PI)

#define RSUN  8.3          
#define ZSUN  0.006      

#define DMAX  25.0

/* Step size in kpc */
#define STEP  0.01



void radec_to_lb(double ra_deg, double dec_deg, double *gl, double *gb) {
   
    const double ra_ngp  = 192.8595 * D2R;
    const double dec_ngp =  27.1284 * D2R;
    const double l_ncp   = 122.9320 * D2R;

    double ra  = ra_deg  * D2R;
    double dec = dec_deg * D2R;

    double sd = sin(dec), cd = cos(dec);
    double sn = sin(dec_ngp), cn = cos(dec_ngp);

    double sb = sd * sn + cd * cn * cos(ra - ra_ngp);
    double b  = asin(sb);

    double y  = cd * sin(ra - ra_ngp);
    double x  = sd * cn - cd * sn * cos(ra - ra_ngp);
    double l  = l_ncp - atan2(y, x);

    /* Normalise l to [0, 2pi) */
    while (l < 0)        l += 2.0 * M_PI;
    while (l >= 2*M_PI)  l -= 2.0 * M_PI;

    *gl = l * R2D;
    *gb = b * R2D;
}



static double ne1(double R, double z) {
    const double n1  = 0.01650;  /* cm^-3 */
    const double A1  = 17.626;   /* kpc   */
    const double B1  =  0.514;   /* kpc   */
    const double C1  =  0.311;   /* kpc   */

    double g1 = (1.0 + cos(M_PI * R / A1)) / 2.0;
    if (R > A1) g1 = 0.0;

    double sech2 = 1.0 / cosh(z / B1);
    sech2 *= sech2;

    double sech2c = 1.0 / cosh(z / C1);
    sech2c *= sech2c;

    return n1 * g1 * (sech2 + sech2c);
}

/*
 * Thick disk — component 2  (Eq. 3)
 */
static double ne2(double R, double z) {
    const double n2  = 0.1200;
    const double K2  = 1.670;
    const double A2  = 17.626;   /* kpc */
    const double B2  =  0.940;   /* kpc */

    double g2 = (1.0 + cos(M_PI * R / A2)) / 2.0;
    if (R > A2) g2 = 0.0;

    double sech = 1.0 / cosh(K2 * z / B2);
    double sech2 = sech * sech;

    return n2 * g2 * sech2;
}

/*
 * Spiral arms — component 3 (simplified; uses 5 arms from YMW16 Table 1)
 */
typedef struct {
    double n;       /* peak density cm^-3 */
    double r0;      /* fiducial radius kpc */
    double theta0;  /* fiducial angle rad  */
    double ka;      /* inverse pitch       */
    double w;       /* width kpc           */
    double C;       /* arm elongation      */
} Arm;

static const Arm arms[5] = {
    /* arm 1 – Norma */
    { 0.1350, 3.048, 0.77*M_PI, 4.25, 0.350, 1.0 },
    /* arm 2 – Carina-Sagittarius */
    { 0.1140, 3.048, 0.25*M_PI, 4.25, 0.350, 0.7 },
    /* arm 3 – Perseus */
    { 0.1150, 4.200, 2.64*M_PI, 4.89, 0.600, 1.0 },
    /* arm 4 – Crux-Scutum */
    { 0.1800, 3.048, 1.77*M_PI, 4.25, 0.350, 1.0 },
    /* arm 5 – Local (Orion spur) */
    { 0.1300, 8.700, 2.10*M_PI, 4.25, 0.180, 1.0 },
};

static double ne3(double x, double y, double z) {
    const double H3  = 0.628;  /* scale height kpc */
    double R   = sqrt(x*x + y*y);
    double phi = atan2(y, x);

    double sech = 1.0 / cosh(z / H3);
    double en3  = 0.0;

    for (int i = 0; i < 5; i++) {
        const Arm *a = &arms[i];
        /* log-spiral centre at angle theta for radius R */
        double theta_arm = a->theta0 + a->ka * log(R / a->r0);
        /* angular distance to arm */
        double dtheta = phi - theta_arm;
        /* wrap to (-pi, pi) */
        while (dtheta >  M_PI) dtheta -= 2*M_PI;
        while (dtheta < -M_PI) dtheta += 2*M_PI;
        /* perpendicular distance to arm centre */
        double d = R * fabs(sin(dtheta));
        double contrib = a->n * exp(-d*d / (a->w * a->w)) * sech * sech;
        en3 += contrib;
    }
    return en3;
}

/*
 * Galactic Centre — component 4
 */
static double ne4(double x, double y, double z) {
    const double n4  = 10.0;
    const double A4  =  0.550;
    const double H4  =  0.026;

    double R = sqrt(x*x + y*y);
    double sech = 1.0 / cosh(R / A4);
    double sech2 = sech * sech;
    double sechz = 1.0 / cosh(z / H4);

    return n4 * sech2 * sechz * sechz;
}


static double ne_total(double x, double y, double z) {
    double R = sqrt(x*x + y*y);
    double n = ne1(R, z) + ne2(R, z) + ne3(x, y, z) + ne4(x, y, z);
    if (n < 0) n = 0;
    return n;
}


double ymw16_dm_to_dist(double gl_deg, double gb_deg, double dm) {
    double l = gl_deg * D2R;
    double b = gb_deg * D2R;

    /* Unit vector from Sun in Galactocentric frame */
    double cl = cos(l), sl = sin(l);
    double cb = cos(b), sb = sin(b);

    /* Sun position in GC frame: (RSUN, 0, ZSUN) */
    double sx = RSUN, sy = 0.0, sz = ZSUN;

    /* Direction cosines (GC frame, x toward GC from Sun) */
    double dx = -cl * cb;   /* negative because l=0 points to GC */
    double dy =  sl * cb;
    double dz =  sb;

    double dm_acc = 0.0;
    double dist   = 0.0;

    while (dist < DMAX) {
        double x = sx + dx * dist;
        double y = sy + dy * dist;
        double z = sz + dz * dist;

        double ne = ne_total(x, y, z);  
        dm_acc += ne * STEP * 1000.0;

        if (dm_acc >= dm) {
            double overshoot = dm_acc - dm;
            double back = (ne > 0) ? (overshoot / (ne * 1000.0)) : 0.0;
            return dist - back;
        }

        dist += STEP;
    }

    return -1.0;
}
