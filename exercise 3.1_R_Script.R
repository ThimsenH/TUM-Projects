######################################### INITIALISING VECTORS ################################################
# define x-sample
x=c(0.5,0.6,1,1.4,1.8,3.6,5.7,6.4,13)  

# define y-sample
y=c(5,28,68,77,48,48,98,96,99)  

########################################### REGRESSION MODEL ##################################################
# linear regression model(z): regress y on x
z=lm(y~x)			

# output linear regression model z
z				        

# output of z
summary(z)		


############################################### ERRORS ########################################################
#The RSS
sum(z$residuals^2)  
