#ifndef YMW16_H
#define YMW16_H

/*
 * ymw16.h — Minimal C implementation of the YMW16 electron-density model.
 *
 * Reference:
 *   Yao, Manchester & Wang (2017), ApJ 835, 29
 *   https://doi.org/10.3847/1538-4357/835/1/29
 *
 * This is a self-contained, dependency-free implementation of the
 * key Galactic components used to convert DM -> distance.
 *
 * Units throughout: distances in kpc, DM in pc cm^-3.
 */

/* Convert equatorial J2000 (degrees) to Galactic (degrees). */
void radec_to_lb(double ra_deg, double dec_deg, double *gl, double *gb);

/*
 * DM -> distance using YMW16.
 * Returns distance in kpc, or -1 if DM exceeds model maximum.
 */
double ymw16_dm_to_dist(double gl_deg, double gb_deg, double dm);

#endif /* YMW16_H */
