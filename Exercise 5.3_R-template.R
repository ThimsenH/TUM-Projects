library(tidyverse)

train = read_csv("loan-train.csv")
test = read_csv("loan-test.csv")

train <- train %>%
  mutate(age = case_when(
    age <= 25 ~ "<=25",
    age > 25 & age <= 39 ~ "25-39",
    age > 40 & age <= 59 ~ "40-59",
    age > 60 ~ "60+",
    TRUE ~ "NA"
  ))

test <- test %>%
  mutate(age = case_when(
    age <= 25 ~ "<=25",
    age > 25 & age <= 39 ~ "25-39",
    age > 40 & age <= 59 ~ "40-59",
    age > 60 ~ "60+",
    TRUE ~ "NA"
  ))

###############
##	a)	##	
##############

# library for naive Bayes
library(e1071)

# create table to append error rates for each attribute when used to create rule
table_1rule <- data.frame(matrix(ncol = 2, nrow = 0))
colnames(table_1rule) <- c("attribute", "errorRate")

# loop through attributes and append to table from above
for (i in 2:15) {
  train_subdata <- train %>% select(1, i)
  nb2 <- naiveBayes(as.factor(loan) ~ ., data=train_subdata, laplace=1)
  rules <- predict(nb2, train_subdata, type="class")
  errorRate = nrow(train_subdata %>% filter(loan!=rules))/nrow(train_subdata)
  table_1rule[nrow(table_1rule) + 1,] <- list(colnames(train[,i]), errorRate)
  rm(errorRate, i, rules, train_subdata, nb2)
}
table_1rule

###############
##	b)	##	
##############

# create naive Bayes prediction model
nb <- naiveBayes(as.factor(loan) ~ ., data=train, laplace=1)

# predict "loan" attributes for test dataset
predictions = predict(nb, test, type="class")

# create confusion matrix
confMat <- table(true=test$loan,prediction=data.frame(predictions)$predictions)
confMat

# calculate error rate
errorRate = nrow(test %>% filter(loan!=predictions))/nrow(test)
errorRate

###############
##	c)	##	
##############