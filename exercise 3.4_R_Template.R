########################################### Setting up the data frame #################################################

library(AER)  #install.packages("AER")

data("CPS1988")

?CPS1988

summary(CPS1988)

# experience is not observed, but calculated and therefore, sometimes negative or zero

attach(CPS1988)  # attach "journal" data set st. R knows all the relevant variables 

summary(wage)

head(wage)       # wage is numeric, decimal number and has no single value twice 



########################################## Interactions ###############################################################

model_int=lm(log(wage)~experience+I(experience^2)+education*ethnicity)  # includes interaction (:) and main efffects

summary(model_int)