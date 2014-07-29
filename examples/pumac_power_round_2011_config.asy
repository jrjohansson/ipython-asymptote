import cse5;
import olympiad;
size(100);

/* Setup for cse5 default pens */
pointpen = black;
pathpen = linewidth(1.5);
dotfactor = 7;

/* Some other common pens to use */
pen darkgreen = linewidth(1.5),
    darkred = linewidth(1) + red,
    darkblue = linewidth(1) + rgb(0, 0, 0.7),
    faded = linewidth(1) + linetype("0 4"),
    dots = linewidth(1)+ dotted;

/* Define points and paths described in the general problem setting */
pair B = (0,0), C = (10,0), A = (2,7);
path t = A--B--C--cycle, incirc = incircle(A,B,C);
pair I = incenter(A,B,C), D = foot(I,B,C), E = foot(I,C,A), F = foot(I,A,B), P = (4.6,1);
pair A1 = extension(B,C,A,P), B1 = extension(A,C,B,P), C1 = extension(A,B,C,P);
pair X1 = reflect(I,A1)*D, Y1 = reflect(I,B1)*E, Z1 = reflect(I,C1)*F;
pair P1 = extension(A,X1,B,Y1), V = extension(A1,X1,A,C), A2 = extension(A,X1,B,C);
pair A0 = extension(Y1,Z1,E,F), B0 = extension(X1,Z1,D,F), C0 = extension(X1,Y1,D,E);
pair R = (1.5*A + 3.5*C)/5, S = extension(A0,R,A,B), T = extension(C0,R,B,C);
pair P2 = extension(A0,T,B0,R), M = extension(A,B,A0,C), N = extension(A,C0,B,C);

/* Draw a couple of the common paths */
D(A--B--C--cycle); D(incircle(A,B,C));

/* Label some of the common points */
D(MP("A", A, NE));
D(MP("B", B));
D(MP("C", C));
D(MP("I", I, W));