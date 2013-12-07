
  X = as.matrix(all.rdm)
# PCA "by hand"
  U.hat = matrix.sqrt.inv.pc(cov(X))
  Z.hat = X %*% t(U.hat)

# see % variation of PCs (before scaling) 
  cumsum(eigen(cov(X), symmetric=TRUE)$values) / sum(eigen(cov(X), symmetric=TRUE)$values)

# if you only want to use the first 'k' PCs you'll need to run this code:
# k = ???
# Z.hat =  Z.hat[,1:k]
# d = k
 
# Estimation:

# Set number of Lags, supply weight vector  
  L = 8
  d = 3
# Weight matrix  
	p = d*(d-1)/2 ; p2 = 2*p
  	phi = 1 - (0:L)/(L+1) ; phi.total = sum(phi) ; phi = phi / phi.total
   PHI = c( rep(phi[1],p), rep(phi[-1],each = p2) )   

# Initialization for optimization 
#  theta.ini = as.matrix(numeric(p))

# In parctice user should try several random initializations

# Generate some random starting values using a latin hypercube based spacing
  require(tgp)
  nStart = 30000 # number of starting values to try, make this is large as you can stand
  startingValues = latin.hc(d,n.inits = nStart)
  startingObj = numeric(nStart)

  
for(i in 1:nStart){
  startingObj[i] = DOCInVAR(theta_s = as.vector(startingValues[,i]), Z_s = Z.hat, L_s = L, PHI_s = PHI, C_s= 2.25)
}



# didn't complete
startingObjCompleted <- startingObj[which(!startingObj==0)]


theta_r <- as.numeric(theta_s)
theta <- theta_r

Z <- as.matrix(Z.hat)
d <- as.numeric(ncol(Z.hat))
L <- as.numeric(L)
n <- as.numeric(nrow(Z.hat))

PHI <- as.matrix(PHI)

C_s <- as.numeric(2.25)

Iden <- diag(d)

k <- 0

W <- matrix(NA, d, d)
W <- diag(d)

for(j in 1:(d-1)){
	for(i in ((j+1):d)){				
    Q <- matrix(NA, d, d)
	Q <- diag(d)
    c_f <- cos(theta[k+1])
    s <- sin(theta[k+1])
    Q[i-1,i-1] = c_f
		Q[j-1,j-1] = c_f
		Q[i-1,j-1] = -s
    Q[j-1,i-1] = s
    W = Q %*% W
		k <- k+1		
	}#end inner for		
}#end outer for 

tW <- t(W)
S <- Z%*%tW
SH <- abs(S)

for(j in 1:(d)){
  for(i in 1:(n)){
    sTemp <- SH[i,j];
    if(sTemp <= C_s){
      SH[i,j] = sTemp*sTemp
    }
    if(sTemp > C_s){
      SH[i,j] = 2*C_s*sTemp - C_s*C_s
    }
  }
}

ColMeans <- colMeans(SH)

z <- 0
ans <- 0.0; 
b <- (d*(d-1))/2 + L*d*(d-1)

out <- as.vector(b)

#//Lag 0. A total of d(d-1)/2 entries in out will be filled. i and j are column numbers. k is row number 
for(i in 1:(d)){	

	for(j in (i+1):(d)){
		
		if (j <= d) {
		ans = 0.0 #; //next column so restart 
		ans = crossprod(SH[,i],SH[,j]) #dot(SH.col(i), SH.col(j));							
		out[z] = ans/n - ColMeans[i]*ColMeans[j] #; //adjust by cross mean and store in out 			
		z = z+1		
		}
	} #//end j for
} #//end i for  -- END Lag 0

#//z now contains the index of the next position for outptr
#/**Lag 1 and above. */
  
	for(lag in 1:L) { #int lag=1;lag<=L;lag++){		
		for(i in 1:(d)){  #=0;i<d;i++){	
			for(j in 1:(d)) { #=0;j<d;j++){			
				ans=0.0
				
				if(i!=j){      
						#// A.submat(p, r, q, s)	A.submat(first_row, first_col, last_row, last_col)       
						ans = crossprod(SH[1:(n-lag),i],SH[lag:(n-1),j]) #(SH.submat(0,i,n-lag-1,i), SH.submat(lag,j,n-1,j));							
						out[z] = ans/n - ColMeans[i]*ColMeans[j]  #; //adjust by cross mean and store in out 			
						z <- z+1 #z++;
					}else{ 
					#	//Do nothing				
					}# //end if-else 			
			} #//end j for	-- Finished column in 2nd matrix. Move to next one. 
		} #//end i for -- Finished with column in 1st matrix. Move to next one. 
} #//end lag for. Finished calculations for this lag. Next lag. 
	
obj = crossprod((out * PHI), out)
obj
}