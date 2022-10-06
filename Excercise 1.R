setwd("~/Desktop/Uni/Master/BA & ML/Übung 1")
library(tidyverse)
'Exercise 1.1' 
# a)
df_import <- read.csv("LaborSupply1988.csv")
df <- as_tibble(df_import)

# b)
ncol(df)
nrow(df)
# or:
dim(df)
# => 5 columns, 532 rows

# c)
names(df)

# d)
head(df, h = 2)

# e)
range(df$age)

# f)
grouped <- group_by(df, kids)

summarise(grouped, mean_hours = mean(lnhr))

# g)
filtered <- filter(df, age == 40) %>% summarise(mean_kids = mean(kids))

'Exercise 1.2'
# a)
hist(df$age)

# b)
group_by(df,age) %>% summarise(mean_kids=mean(kids)) %>% plot()
cor(df$kids, df$age)

# c)
plot(df$age, df$lnwg)

# d)
group_by(df,age) %>% summarise(mean_hour=mean(lnwg)) %>% plot()
cor(df$lnwg, df$age)

# e)
plot(df$lnhr, df$age, pch = as.numeric(df$disab), col=c("green", "red"))

# f)
boxplot(df$lnhr ~ df$kids)
hist(df$kids, breaks = (max(df$kids) - min(df$kids)))

'Exercise 2.1'
library(tidyverse)

# a)
octoberfest <- read.csv("Oktoberfest.csv")
oct <- as_tibble(octoberfest)

# b)
names(oct)

# c)
# Base R Solution
oct[oct$Year == 1995,]$Beer_Price

# Tidyverse Solution
oct %>% filter(Year == 1995) %>% select(Beer_Price)

# d)
min(oct$Year)
'1985'

# e)
# Tidyverse Solution
summarize(oct, min_vis = min(Visitors_Total), max_vis = max(Visitors_Total))

# Base R Solution
min(oct$Visitors_Total)
max(oct$Visitors_Total)
range(oct$Visitors_Total)

# f)
plot(oct$Year, oct$Beer_Consumption, type = 'line')
# or
ggplot(oct, aes(x = Year, y = Beer_Consumption)) + geom_line()

# g)
plot(oct$Year, oct$Visitors_Total, type = 'line')
# or
ggplot(oct, aes(x = Year, y = Visitors_Total)) + geom_line()

cor(oct$Visitors_Total, oct$Beer_Consumption)

'Exercise 2.2'
# a)
oct %>% filter(Year >= 2000, Year <= 2007) %>% summarize(avg_price = mean(Beer_Price))

# b)
oct %>% filter(Year >= 2000, Year <= 2007) %>% summarize(var_price = var(Beer_Price))

# c)
oct = oct %>% mutate(difference = Beer_Price - lag(Beer_Price))

# d)
ggplot(tail(oct, -1), aes(x = Year, y = difference)) + geom_line()








