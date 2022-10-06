# Business Analytics WS 2019/2020
# Generalized Linear Models - Exercise

# Load the library tidyverse
library(tidyverse)

# Load the data from the file admit-train.csv
train = read_csv("admit-train.csv")

names(train) 	
# "admit" (acceptance for master course) = 1 means success of admission. 0 does failure.  
# "gre", "gpa" (points in exams): 
	# GRE: Graduate Record Examinations e (200, 800) 10 point increments
	# GPA: Grade Point Average e (2, 4) (4 is best GPA)
# "rank" (rank of bachelor university ) = e (1, ..., 4) 1 point increments (1 is best rank)

summary(train$admit)
summary(train$gre)
summary(train$gpa)
summary(train$rank)
summary(as.factor(train$rank))

###############
##	a)	##	
##############

# visualize relationships
plot(admit ~ gre, data=train,pch="+")
plot(admit ~ gpa, data=train,pch="+")
plot(admit ~ rank, data=train,pch="+")

# visualise distributions
hist(train$gre, breaks=25)
hist(train$gpa, breaks=18)

## Generalized Linear Model (GLM) (Logistic Regression) 
mylogit = glm(admit ~ gre + gpa + as.factor(rank), data=train, family=binomial(link="logit"))
summary(mylogit)

###############
##	b)	##	
##############


##############
##	c)	##
##############


##############
##	d)	##	
##############

# Packages: aod 

library(aod)

wald.test(b=coef(mylogit), Sigma=vcov(mylogit), Terms=4:6)	# similar to F-test in multiple linear regression analysis

##############	 
##	e)	##	
##############

rank = c(1,2,3,4)
gre = c(mean(train$gre))
gpa = c(mean(train$gpa))
myinstances = data.frame(gre,gpa,rank)
myinstances

# add predictions to data frame 
myinstances$pAdmit = predict(mylogit, newdata=myinstances, type="response")
myinstances

##############
##	f)	##
##############

MCFad = 1 - (mylogit$deviance/mylogit$null.deviance)
MCFad	

##############
##	g)	##
##############

test = read_csv("admit-test.csv") 
preds = predict(mylogit, newdata=test, type='response')
preds

##############
##	h)	##
##############

test = test %>% mutate(pred = round(preds)) 
test %>% group_by(admit, pred) %>% summarise(count=n())

# you can also create confusion matrix as below
table(true=test$admit,prediction=round(preds))

## error rate of Logit-Model ##
incorrectPredictionCount = nrow(test %>% filter(admit!=pred))
totalPredictions = nrow(test)
errorRate = incorrectPredictionCount/totalPredictions
errorRate