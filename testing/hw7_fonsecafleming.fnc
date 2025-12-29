########################################################################
#  Template: Input File for GimOPT v03                                 #
#                                                                      #
#    Hongbing Fang                                                     #
#    Mechanical Engineering and Engineering Science                    #
#    University of North Carolina at Charlotte                         #
#    March 22, 2007                                                    #
#                                                                      #
#  Format: 1. '*' starts a line of a key word                          #
#          2. '#' or '$' starts a line of comments                     #
#          3. All problems are defined as Minimization problems        #
#          4. Inequality constraints are in the form g(x) <= 0         #
#          5. All keywords and sympols are case insensitive            #
#          6. The order of sections (or keywords) cannot be changed    #
#          7. Variable and function numbers are in increasing order    #
#          8. All function definitions end with ';'                    #
#                                                                      #
########################################################################


#-----------------------------------------------------------------------
#  Design variables
#  	X1: LOWER-BOUND, UPPER-BOUND, TYPE, ACCURACY
#       ...
#  	Xm: LOWER-BOUND, UPPER-BOUND, TYPE, ACCURACY
#
#     NOTE: 1. The number of variables is given after keyword '*VARIABLE'
#           2. Variable type is 'INT" or 'REAL'
#           3. Accuracy is optional. An integer varible has an accuracy
#              of 1. If not specified, default accuracy will be used for
#              a real variable.
#-----------------------------------------------------------------------

*VARIABLE: 2

X1:  -4,    4,      REAL,      0.000001
X2:  -4,    4,      REAL,      0.000001


#-----------------------------------------------------------------------
#  Optimization Formulation
#  	O1 = ( ... );          \
#       ...                |---> Objectives
#  	Op = ( ... );          /
#
#  	EC1 = ( ... );         \
#       ...                |---> Equality constraints
#  	ECq = ( ... );         /
#
#  	INEC1 = ( ... );       \
#       ...                |---> Inequality constraints
#  	INECr = ( ... );       /
#
#     NOTE: 1. The numbers after keywords are the number of objectives,
#              eqality constraints, and inequality constraints, respectively
#           2. The oprators in these formulations are limited to
#                  +   -   (   )
#              since gradient functions also need to be formulated.
#           3. Only functions (F1, F2 ...) are allowed to appear in the
#              formulation; no variables and standard functions can appear
#              in the formulation (as they affect gradient formulation).
#              Constants can be multiplied to a function, but not added to.
#              For example, 0.5*F1 + 0.2*F2 is OK, but not F1 + 0.5
#           4. '=' can be replace with ':'
#-----------------------------------------------------------------------

*OBJECTIVE: 2
O1 = F1;
O2 = F2;

*EQUALITY-CONSTRAINT: 0


*INEQUALITY-CONSTRAINT: 0



#-----------------------------------------------------------------------
#  All functions including both objective and constraint functions
#  	F1 = ( ... );
#       ...
#  	Fn = ( ... );
#
#     NOTE: 1. The number after the keyword is the number of functions
#           2. '=' can be replace with ':'
#-----------------------------------------------------------------------

*FUNCTION: 2

F1 = 1 - EXP(-(X1 - (1/SQRT(2)))^2 - (X2-(1/SQRT(2)))^2);
F2 = 1 - EXP(-(X1 + (1/SQRT(2)))^2 - (X2+(1/SQRT(2)))^2);

#-----------------------------------------------------------------------
#  Gradients of all of the above functions
#  	GF1-X1 = ( ... );
#       ...
#  	GF1-Xm = ( ... );
#
#  	GF2-X1 = ( ... );
#       ...
#  	GF2-Xm = ( ... );
#
#           ...
#
#  	GFn-X1 = ( ... );
#       ...
#  	GFn-Xm = ( ... );
#
#     NOTE: '=' can be replace with ':'
#-----------------------------------------------------------------------

#*GRADIENT

#GF1-X1 = -(-2*X1 + SQRT(2))*EXP(-(X1 - SQRT(2)/2)^2 + (X2 - SQRT(2)/2)^2);
#GF1-X2 =  -(2*X2 - SQRT(2))*EXP(-(X1 - SQRT(2)/2)^2 + (X2 - SQRT(2)/2)^2);

#GF2-X1 = -(-2*X1 - SQRT(2))*EXP(-(X1 + SQRT(2)/2)^2 + (X2 + SQRT(2)/2)^2);
#GF2-X2 =  -(2*X2 + SQRT(2))*EXP(-(X1 + SQRT(2)/2)^2 + (X2 + SQRT(2)/2)^2);



#-----------------------------------------------------------------------
# End of input file
#-----------------------------------------------------------------------
