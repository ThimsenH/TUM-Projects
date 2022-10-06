######################################### INITIALISING VECTORS ################################################

demand=c(28.20, 37.65, 47.28, 59.76, 73.44, 86.19, 100.31, 112.58, 121.63)  # define demand sample

t=c(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)                                       # define period sample

t_a=c(0, 1, 2, 3, 4, 5, 6, 7, 8)                                            # define adjusted period sample with same number of time units as demand sample


########################################### REGRESSION MODEL ##################################################

# define linear regression model (model): regress demand on period (adjusted)
model=lm(demand~t_a)  		                                                  
# output of linear regression model (model) 
model				                                                                
summary(model)		

############################################# PREDICTIONS #####################################################
# define predicted values of model
pm=predict(model) 
#pm=predict(model,newdata=data.frame(t_a=t))    
# output predicted values of model 
pm
# output predicted values for t=9 and t=10
predict(model, data.frame(t_a = c(9,10)))

############################################### ERRORS ########################################################
# define prediction errors
pe=c(pm-demand)        
# output prediction errors
pe                

# define mean squared error
MSE=sum((pe)^2)/length(pe)  
#MSE=sum(model$residuals^2/length(d))  #Alternatively calculate MSE directly from lm
# output mean squared error
MSE                         

# define root mean squared error
RMSE=sqrt(MSE)              
# output root mean squared error
RMSE                        

############################################# BIANNUAL COMPONENT #############################################
# define biannual component 
q = c(rep(1,9)) 

for (i in c(1:length(q))) { 
  if(i%%2==0) {
    q[i]=0
    }
  }

#fit the regression model
model_new=lm(demand~t_a + q) 
# output predicted values for t=9 and t=10
predict(model_new, data.frame(t_a = c(9,10), q = c(0,1)))

#output model
model_new
#summary of the model
summary(model_new)
