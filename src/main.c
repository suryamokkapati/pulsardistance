File Edit Options Buffers Tools C Help                                                                                                                                                                                                                                                                                      
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "../ymw16/ymw16.h"

#define BOX_WIDTH 40

static void print_box(void) {
    const char *title = "PULSAR DISTANCE UTILITY";
    int title_len = (int)strlen(title);
    int pad_left  = (BOX_WIDTH - 2 - title_len) / 2;
    int pad_right = (BOX_WIDTH - 2 - title_len) - pad_left;

    printf("\n+");
    for (int i = 0; i < BOX_WIDTH - 2; i++) printf("-");
    printf("+\n");

    printf("|%*s%s%*s|\n", pad_left, "", title, pad_right, "");

    printf("+");
    for (int i = 0; i < BOX_WIDTH - 2; i++) printf("-");
    printf("+\n\n");
}

static int read_double(const char *prompt, double *out) {
    char buf[64];
    printf("%s", prompt);
    if (!fgets(buf, sizeof(buf), stdin)) return 0;
    char *end;
    double v = strtod(buf, &end);
    if (end == buf) return 0;
    *out = v;
    return 1;
}

int main(void) {
    print_box();

    double ra, dec, dm;

    if (!read_double("Right Ascension (degrees, J2000): ", &ra)) {
        fprintf(stderr, "Error: invalid RA.\n");
        return 1;
    }
    if (!read_double("Declination     (degrees, J2000): ", &dec)) {
        fprintf(stderr, "Error: invalid Dec.\n");
        return 1;
    }
    if (!read_double("Dispersion Measure (pc/cm^3):     ", &dm)) {
        fprintf(stderr, "Error: invalid DM.\n");
        return 1;
    }

    /* Convert RA/Dec (J2000) -> Galactic l, b */
    double gl, gb;
    radec_to_lb(ra, dec, &gl, &gb);

    printf("\nGalactic longitude l = %.4f deg\n", gl);
    printf("Galactic latitude  b = %.4f deg\n", gb);

    /* Run YMW16 */
    double dist_kpc = ymw16_dm_to_dist(gl, gb, dm);

    if (dist_kpc < 0) {
        fprintf(stderr, "\nYMW16: DM exceeds model maximum along this line of sight.\n");
        fprintf(stderr, "The pulsar likely lies beyond the modelled Galaxy edge.\n");
        return 1;
    }

    printf("\n--- YMW16 Result ---\n");
    printf("Distance : %.3f kpc  (%.1f pc)\n", dist_kpc, dist_kpc * 1000.0);
    printf("\n");

    return 0;
}



