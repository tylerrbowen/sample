# works through spx/csco/ibm ex. from Dynamic Orthagonal Components paper
# 	notes:
#		- Tsay price series for the tickers varies from other sources.  This uses Tsay data to match
#		- Using restriction of initial VAR as understood from paper doesn't match w/ published results
#			Expect this is typo in paper as matched w/ little modification
#		- Uses R implementation of rcpp function.  SLOW.  If ever prod. need to get rcpp working on Win32 sys.


WD = "C:/users/tyler/desktop/r workfiles/doc work/DynamicOrthagonalComponents"
setwd(WD)

source("Support_funcs.r")
source("DOCInVar.r")
source("DOC_Test_Stat.r")

library(vars)
library(portes)
library(fGarch)
library(fBasics)
library(quantmod)
library(PerformanceAnalytics)
require(tgp)

#### BELOW PULLS Ex. DATA/ HOWEVER TSAY STOCK PRICES IN SERIES DIFFERENT!! #####
# # # SP500 = getYahoo("^GSPC")
# # # CSCO = getYahoo("CSCO")
# # # INTC = getYahoo("INTC")	

# # # CSCO = window(CSCO, "1991-01-02","1999-12-31")
# # # INTC = window(INTC, "1991-01-02","1999-12-31")
# # # SP500 = window(SP500,"1991-01-02","1999-12-31")
# # # CSCO = CSCO[,"CSCO.Adj.Close"]
# # # INTC = INTC[,"INTC.Adj.Close"]
# # # SP500= SP500[,"^GSPC.Adj.Close"]
# # # names(CSCO) <- "CSCO"
# # # names(INTC) <- "INTC"
# # # names(SP500) <- "SP500"

# # # CSCO.R <- returns(CSCO, percentage=TRUE, trim=TRUE)
# # # INTC.R <- returns(INTC, percentage=TRUE, trim=TRUE)
# # # SP500.R <- returns(SP500, percentage=TRUE, trim=TRUE)

# # # CSCO.RDM <- CSCO.R - mean(CSCO.R)
# # # INTC.RDM <- INTC.R - mean(INTC.R)
# # # SP500.RDM <- SP500.R - mean(SP500.R)

# # # all <- merge(SP500, CSCO)
# # # all <- merge(all, INTC)


# # # basicStats(all, ci = 0.95)
# # # cor(all)

# # # all.r <- merge(SP500.R, CSCO.R)
# # # all.r<-merge(all.r,INTC.R)

# # # basicStats(all.r, ci = 0.95)
# # # cor(all.r)

tsay_stock_ret_series <- read.delim("tsay_stock_ret_series.txt")
dts <- tsay_stock_ret_series[,1]
dts <- as.POSIXct(dts)
tsay_stock_ret_series[,1] <- dts
stock_ret_series.xts <- as.xts(tsay_stock_ret_series[,-1],order.by=tsay_stock_ret_series[,1])
basicStats(stock_ret_series.xts)

                     # # # # # # sp        csco        intc
# # # # # # nobs        2275.000000 2275.000000 2275.000000
# # # # # # NAs            0.000000    0.000000    0.000000
# # # # # # Minimum       -7.114000  -22.100000  -14.581000
# # # # # # Maximum        4.990000   15.576000   12.850000
# # # # # # 1. Quartile   -0.359000   -1.445500   -1.321000
# # # # # # 3. Quartile    0.521500    2.045000    1.734000
# # # # # # Mean           0.065609    0.256708    0.156076
# # # # # # Median         0.048000    0.274000    0.104000
# # # # # # Sum          149.261000  584.011000  355.072000
# # # # # # SE Mean        0.018338    0.059836    0.051669
# # # # # # LCL Mean       0.029648    0.139370    0.054753
# # # # # # UCL Mean       0.101571    0.374047    0.257398
# # # # # # Variance       0.765072    8.145232    6.073472
# # # # # # Stdev          0.874684    2.853985    2.464442
# # # # # # Skewness      -0.359778   -0.396043   -0.235158
# # # # # # Kurtosis       6.038931    3.717029    2.465302

cor(stock_ret_series.xts)

            # # # # # # sp      csco      intc
# # # # # # sp   1.0000000 0.5159069 0.5025471
# # # # # # csco 0.5159069 1.0000000 0.4732159
# # # # # # intc 0.5025471 0.4732159 1.0000000




# PAPER SUGGESTS THE FOLLOWING, HOWEVER DOES NOT MATCH
# # # # # # # var.r.1.uc <- VAR(stock_ret_series.xts, p=5, type="none")
# # # # # # # var.stocks <- VAR(stock_ret_series.xts, p=5,ic="AIC")
# # # # # # # restriction_mat_init <- matrix(c(0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,1,
							# # # # # # # 0,0,0,1,1,0,0,0,0,0,0,0,1,0,0,1,
							# # # # # # # 1,0,1,0,0,0,0,0,0,0,0,0,1,0,0,1), nrow = 3, ncol = 16, byrow = TRUE)	
# # # # # # # var.restrict.stocks <- restrict(var.stocks, method = "manual", resmat = restriction_mat_init)
# # # # # # # LjungBox(stock.resid)

# WHAT MUST BE ACTUAL VAR STRUCTURE IN ORDER TO MATCH RESULTS
stock_ret_series.dm <- stock_ret_series.xts - mean(stock_ret_series.xts)
var.stocks.dm <- VAR(stock_ret_series.dm , p=5,ic="AIC")
summary(var.stocks.dm)

restriction_mat_dm_new <- matrix(c(1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,1,
							0,0,0,1,1,0,0,0,0,0,0,0,1,0,0,1,
							1,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0), nrow = 3, ncol = 16, byrow = TRUE)
							
var.restrict.stocks.dm <- restrict(var.stocks.dm , method = "manual", resmat = restriction_mat_dm_new)
residual.dm <- resid(var.restrict.stocks.dm)
LjungBox(residual.dm)


# Directly from Matteson materials
# Run through Sim.
X = as.matrix(residual.dm)
# PCA "by hand"
U.hat=matrix.sqrt.inv.pc(cov(X))
Z.hat = X %*% t(U.hat)

# see % variation of PCs (before scaling) 
cumsum(eigen(cov(X), symmetric=TRUE)$values) / sum(eigen(cov(X), symmetric=TRUE)$values)

# Estimation:

# Set number of Lags, supply weight vector  
L = 1 # try w/ 1, great # start pts.
d = 3
# Weight matrix  
p = d*(d-1)/2 ; p2 = 2*p
phi = 1 - (0:L)/(L+1) ; phi.total = sum(phi) ; phi = phi / phi.total
PHI = c( rep(phi[1],p), rep(phi[-1],each = p2) )   

# Initialization for optimization 
# theta.ini = as.matrix(numeric(p))

# In parctice user should try several random initializations

# Generate some random starting values using a latin hypercube based spacing
nStart = 30000 # number of starting values to try, make this is large as you can stand
startingValues = latin.hc(d,n.inits = nStart)
startingObjRun2 = numeric(nStart)

# rcpp armadillo pain to get working in windows.  just utilize R for purposes of the example
for(i in 1:nStart){
  startingObjRun2[i] = doc.in.var(theta_s = as.vector(startingValues[,i]), Z_s = Z.hat, L_s = L, PHI_s = PHI, C_s= 2.25)
}

min(startingObjRun2)
which.min(startingObjRun2)
startingValues[,which.min(startingObjRun2)]

# Best initial starting value
theta.ini = as.matrix(startingValues[,which.min(startingObjRun2)])

out = nlminb(start = theta.ini, 
			 objective = doc.in.var,  # Change this to DOCinMean as necessary
		     gradient = NULL, 
			 hessian = NULL, 
			 scale = 1, 
			 control = list(iter.max = 1000, eval.max = 1000), 
		     lower = -pi, 
			 upper = pi, 
			 Z_s = Z.hat, 
			 L_s = L, 
			 PHI_s = PHI, 
			 C_s= 2.25)

theta.hat = out$par  ; theta.hat
W.hat = (theta2W(out$par))  # Separating Matrix
W.hat = canonicalW(W.hat)      
M.hat = t(solve(t(U.hat) %*% t(W.hat)))   # Mixing Matrix
Minv <- solve(M.hat)
Minv
M.hat
S.hat = Z.hat %*% t(W.hat)   # Estimated DOCs (in Var)

DOC_Test_Stat(S.hat, 10)


# Modeling the series
model_1 <- garchFit(~ garch(1,1), data =  S.hat[,1], trace = FALSE, cond.dist="std")
model_2 <- garchFit(~ garch(1,1), data =  S.hat[,2], trace = FALSE, cond.dist="std")
model_3 <- garchFit(~ garch(1,1), data =  S.hat[,3], trace = FALSE, cond.dist="std")

# stds
model_1.sigma <- model_1@sigma.t
model_2.sigma <- model_2@sigma.t
model_3.sigma <- model_3@sigma.t

# vars
model_1.v <- model_1.sigma^2
model_2.v <- model_2.sigma^2
model_3.v <- model_3.sigma^2

# res
model_1.res <- model_1@residuals
model_2.res <- model_2@residuals
model_3.res <- model_3@residuals


all_fit <- cbind(model_1.v, model_2.v, model_3.v)

n <- length(model_1.v)

all_sigma <- cbind(model_1.sigma, model_2.sigma,  model_3.sigma)

all_res <- cbind(model_1.res, model_2.res, model_3.res)

# check the variances and volatilities
LjungBox(all_fit)
LjungBox(all_sigma)


# Build time series of modeled covariance, sd
model_fit_cov <- array(data=NA, c(n, d, d))
model_fit_sd <- array(data = NA, c(n, d))

for (i in 1:n) {
	
	cov_temp <- matrix(NA, d, d)
	cov_temp<- diag(d)
	
	for (j in 1:d) {
		cov_temp[j,j] <- all_fit[i, j]
		
		}
	
	cov_temp <- M.hat %*% cov_temp %*% t(M.hat)
	model_fit_sd[i,] <- sqrt(diag(cov_temp))	
	model_fit_cov[i,,] <- cov_temp
	}
	

lag.dts <- dts	
differ <- length(dts)-length(model_fit_cov[,1,1])
lag.dts <- lag.dts[-c(1:differ)]
	
# covariance xts
model_fit_cov.xts <- as.xts(model_fit_cov[,1,], order.by = lag.dts)
model_fit_cov.xts <- merge(model_fit_cov.xts,as.xts(model_fit_cov[,2,], order.by = lag.dts))
model_fit_cov.xts <- merge(model_fit_cov.xts,as.xts(model_fit_cov[,3,], order.by = lag.dts))

# sd xts
model_fit_sd.xts <- as.xts(model_fit_sd[,1], order.by = lag.dts)
model_fit_sd.xts <- merge(model_fit_sd.xts,as.xts(model_fit_sd[,2], order.by = lag.dts))
model_fit_sd.xts <- merge(model_fit_sd.xts,as.xts(model_fit_sd[,3], order.by = lag.dts))

# build cor
model_fit_cor <- array(data=NA, c(n, d, d))
for (i in 1:n) {
	cor_temp <- matrix(NA, d, d)
	cor_temp<- diag(d)
	cor_temp <- cov2cor(matrix(model_fit_cov[i,,],nrow=3,ncol=3,byrow=TRUE))
	model_fit_cor[i,,] <- cor_temp
	}

# cor xts
model_fit_cor.xts <- as.xts(model_fit_cor[,1,], order.by = lag.dts)
model_fit_cor.xts <- merge(model_fit_cor.xts,as.xts(model_fit_cor[,2,], order.by = lag.dts))
model_fit_cor.xts <- merge(model_fit_cor.xts,as.xts(model_fit_cor[,3,], order.by = lag.dts))


d_count = 60
n <- length(model_fit_cov.xts[,1])-d_count-1
rolling_cov <- array(data=NA, c(n, d, d))
rolling_sd <- array(data=NA,c(n,d))

# Compare modeled to realized
for (i in 1:n) {
	cov_temp <- matrix(NA, d, d)
	cov_temp<- diag(d)
	cov_temp <- cov(tsay_stock_ret_series[i:(60-1+i),-1])
	rolling_sd[i,] <- sqrt(diag(cov_temp))
	rolling_cov[i,,] <- cov_temp
	}

lag.dts <- dts
differ <- length(dts)-length(rolling_cov[,1,1])
lag.dts <- lag.dts[-c(1:differ)]

	
rolling_cov.xts <- as.xts(rolling_cov[,1,], order.by = lag.dts)
rolling_cov.xts <- merge(rolling_cov.xts,as.xts(rolling_cov[,2,], order.by = lag.dts))
rolling_cov.xts <- merge(rolling_cov.xts,as.xts(rolling_cov[,3,], order.by = lag.dts))	

rolling_sd.xts <- as.xts(rolling_sd[,1], order.by = lag.dts)
rolling_sd.xts <- merge(rolling_sd.xts,as.xts(rolling_sd[,2], order.by = lag.dts))
rolling_sd.xts <- merge(rolling_sd.xts,as.xts(rolling_sd[,3], order.by = lag.dts))	


rolling_cor <- array(data=NA, c(n, d, d))
for (i in 1:n) {
	cor_temp <- matrix(NA, d, d)
	cor_temp<- diag(d)
	cor_temp <- cor(tsay_stock_ret_series[i:(60-1+i),-1])
	rolling_cor[i,,] <- cor_temp
	}

rolling_cor.xts <- as.xts(rolling_cor[,1,], order.by = lag.dts)
rolling_cor.xts <- merge(rolling_cor.xts,as.xts(rolling_cor[,2,], order.by = lag.dts))
rolling_cor.xts <- merge(rolling_cor.xts,as.xts(rolling_cor[,3,], order.by = lag.dts))	


chart.TimeSeries(rolling_cor.xts[,c(2,6,7)])

model.column = 1; obs.columns = 2;
model.color = "red"; obs.color = "darkgray"; 

colorset = c(rep(model.color,length(model.column)), 
rep(obs.color, length(obs.columns)))


names(model_fit_cov.xts) <- c("m-spx var", "m-spx-csco covar", "m-spx-intc covar","m-spx-csco covar","m-csco var", "m-csco-intc covar",  "m-spx-intc covar","m-csco-intc covar","m-intc var")
names(model_fit_sd.xts) <- c("m-spx sd", "m-csco sd","m-intc sd")
names(model_fit_cor.xts) <- c("m-spx cor", "m-spx-csco cor", "m-spx-intc cor","m-spx-csco cor","m-csco cor", "m-csco-intc cor",  "m-spx-intc cor","m-csco-intc cor","m-intc cor")

names(rolling_cov.xts) <- c("r-spx var", "r-spx-csco covar", "r-spx-intc covar","r-spx-csco covar","r-csco var", "r-csco-intc covar",  "r-spx-intc covar","r-csco-intc covar","r-intc var")
names(rolling_sd.xts) <- c("r-spx sd", "r-csco sd","r-intc sd")
names(rolling_cor.xts) <- c("r-spx cor", "r-spx-csco cor", "r-spx-intc cor","r-spx-csco cor","r-csco cor", "r-csco-intc cor",  "r-spx-intc cor","r-csco-intc cor","r-intc cor")


# comparison Charts:

chart.TimeSeries(model_fit_sd.xts, colorset = tim6equal,legend.loc="topright",main="modeled sd")
chart.TimeSeries(model_fit_cor.xts[,c(2,3,6)], colorset = tim6equal,legend.loc="topright",main="modeled cor")
chart.TimeSeries(rolling_cor.xts[,c(2,3,6)], colorset = tim6equal,legend.loc="topright",main="rolling cor")

chart.TimeSeries(merge(model_fit_sd.xts,rolling_sd.xts), colorset = tim6equal,legend.loc="topright",main="modeled sd")
chart.TimeSeries(merge(model_fit_sd.xts[,1],rolling_sd.xts[,1]), colorset = tim6equal,legend.loc="topleft",main="modeled sd v 60-d")
chart.TimeSeries(merge(model_fit_sd.xts[,2],rolling_sd.xts[,2]), colorset = tim6equal,legend.loc="topleft",main="modeled sd v 60-d")
chart.TimeSeries(merge(model_fit_sd.xts[,3],rolling_sd.xts[,3]), colorset = tim6equal,legend.loc="bottomleft",main="modeled sd v 60-d")

chart.TimeSeries(merge(model_fit_cor.xts[,2],rolling_cor.xts[,2]), colorset = tim6equal,legend.loc="topleft",main="modeled cor v 60-d")
chart.TimeSeries(merge(model_fit_cor.xts[,3],rolling_cor.xts[,3]), colorset = tim6equal,legend.loc="topleft",main="modeled cor v 60-d")
chart.TimeSeries(merge(model_fit_cor.xts[,6],rolling_cor.xts[,6]), colorset = tim6equal,legend.loc="bottomleft",main="modeled cor v 60-d")

chart.TimeSeries(merge(model_fit_cov.xts[,2],rolling_cov.xts[,2]), colorset = tim6equal,legend.loc="topleft",main="modeled cov v 60-d")
chart.TimeSeries(merge(model_fit_cov.xts[,3],rolling_cov.xts[,3]), colorset = tim6equal,legend.loc="topleft",main="modeled cov v 60-d")
chart.TimeSeries(merge(model_fit_cov.xts[,6],rolling_cov.xts[,6]), colorset = tim6equal,legend.loc="topleft",main="modeled cov v 60-d")
