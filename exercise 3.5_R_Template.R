
library(AER)  #install.packages("AER")
library(plm)  #install.packages("plm")


############################################################ Setting up the data frame ##########################################################

# explicitly take "Grunfeld" from "AER" package, because many different "Grunfeld" data frame versions around

data("Grunfeld",package="AER")  

?Grunfeld

summary(Grunfeld)

############################################################## transform data frame #############################################################

grunfeld = subset(Grunfeld, firm %in% c("General Electric", "General Motors", "IBM"))  # delete all observations but "GE", "GM" and "IBM"

# establish panel data structure with plm()

panel_grunfeld = plm.data(grunfeld, index = c("firm", "year"))   # plm.data defines the indivdual (firm) and time (year) indeces

attach(panel_grunfeld)

summary(invest)

head(invest)          # invest is numeric, decimal number and has no single value twice 

############################################################## create pooled regression model ###################################################


grunfeld_pool = plm(invest~value+capital, data=panel_grunfeld, model="pooling")

# check whether the random effects are really needed
plmtest(grunfeld_pool)  

# create fixed effects model 
grunfeld_fe = plm(invest~value+capital, data=panel_grunfeld, model="within")

# create random effects model
grunfeld_re = plm(invest ~ value + capital, data = panel_grunfeld, model = "random", random.method="walhus") 

# Hausman test to decide between fixed effects model and random effects model
phtest(grunfeld_re, grunfeld_fe)  

