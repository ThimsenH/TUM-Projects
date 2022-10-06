rm(list = ls())
cat("\014") 
library(lmtest)
library(car)
library(tidyverse)

#Read table from Exercise_3.csv
df = read_csv("...path to csv file...")

x1=df$x1
x2=df$x2
y=df$y
x1
x2
y

#a.) Multicollinearity
m1 <- lm(y~x1+x2)
vif(m1)
#Remove x2 (since lower R^2 if we fit model)

#b.) Linearity and fit model
plot(x1,y)
#Quadratic relationship

m <- lm(y~I(x1^2))

#c.) Homoskedasticity
bptest(m)
#Cannot reject H0: Homoskedasticity

#d.) Autocorrelation
plot(x1, m$residuals, type='b')
dwtest(m)
#DW = 3.49 --> negative autocorrelation
#Introduce seasonality

s1 <- rep(0, length(x1))
s1[seq(1, length(s1),2)] = 1
m2 <- lm(y~I(x1^2)+s1)
plot(x1, m2$residuals, type='b')
dwtest(m2)
#DW = 2.08 --> very little autocorrelation

#e.) Exogeneity
#Hausman-Test only for panel data, check correlation with residuals instead
cor(x1,m2$residuals)
#Almost zero --> exogeneity


#Now OLS is BLUE

