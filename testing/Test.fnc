
#-----------------------------------------------------------------------
# Input File Start
#-----------------------------------------------------------------------

        
*VARIABLE: 2

X1:	0.02,	0.06,	REAL,	0.000001
X2:	0.002,	0.008,	REAL,	0.000001

*CONSTANT: 1
k = 5;

*OBJECTIVE: 1

O1 = F1;

*EQUALITY-CONSTRAINT: 0


*INEQUALITY-CONSTRAINT: 2

INEC1 = F2;
#INEC2 = F3;

*FUNCTION: 4
F2 = x1 + x2;
F1 = F2 ** 2;
F3 = Sum(x1, (i, 0, 2));
F4 = x1 * k;

# Gradient function-variable combinations are missing:
#	GF1 (UDF)-X1
#	GF1 (UDF)-X2
# Skipping gradients.


#-----------------------------------------------------------------------
# End of input file
#-----------------------------------------------------------------------
