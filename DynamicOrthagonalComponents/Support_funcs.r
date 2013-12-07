
# Set functions
# David S. Matteson
  # 2011.06.27
  # DOC_support_functions.R
  # Support functions for DOCinMean.R, DOCinVar.R, and DOCinVar_example.R
  # Dynamic Orthogonal Components for Multivariate Time Series, by David S. Matteson and Ruey S. Tsay.
  # Journal of the American Statistical Association Dec 2011, Vol. 106, No. 496: 1450-1463. 

require(tgp)
  
# Generate Mixing matrix for simulations
"Mmix" = function(d){
  M = diag(d)
  M[1,] = rep(1,d)
  for(i in 2:d){
    M[i,(i-1)] = -1
  }
  M
}




"matrix.sqrt" = function(A)
{
  sva = svd(A)
  if (min(sva$d)>=0)
     Asqrt = t(sva$v %*% (t(sva$u) * sqrt(sva$d)))
  else
     stop("Matrix square root is not defined")
  return(Asqrt)
}

"matrix.sqrt.inv" = function(A)
{
  sva = svd(A)
  if (min(sva$d)>=0)
     Asqrt = t(sva$v %*% (t(sva$u) / sqrt(sva$d)))
  else
     stop("Matrix square root is not defined")
  return(Asqrt)
}

"orthogonalize" = function(M)
{
  solve(matrix.sqrt(M%*%t(M)))%*%M
}

pd.vcov.check = function(Sigma){
	dex = NULL
	if(is.na(dim(Sigma)[3])) {
		sva = svd(Sigma)
		temp = min(sva$d)	
		if (min(sva$d)<=0) {dex = c(dex, t)}
	}
	else{ 
		N = dim(Sigma)[3] 
		temp = numeric(N)
		for(t in 1:N){
			sva = svd(Sigma[,,t])
			temp[t] = min(sva$d)
  			if (min(sva$d)<=0) {dex = c(dex, t)}
  		}	
  	}  		
	list(index = dex, min.sv = temp)
}

"matrix.sqrt.inv.pc" = function(A)
{
  evd = eigen(A, symmetric=TRUE)
  Asqrtinv = diag(1/sqrt(evd$values)) %*% t(evd$vectors)
  return(Asqrtinv)
}

"givens.rotation" = function(theta=0, d=2, which=c(1,2))
{
  # David S. Matteson
  # 2008.04.28
  # For a given angle theta, returns a d x d Givens rotation matrix
  #
  # Ex: for i < j , d = 2:  (c -s)
  #                         (s  c)
  c_d = cos(theta)
  s = sin(theta)
  M = diag(d)
  a = which[1]
  b = which[2]
  M[a,a] =  c_d
  M[b,b] =  c_d
  M[a,b] = -s
  M[b,a] =  s
  M
}

"theta2W" = function(theta)
{
  # David S. Matteson
  # 2010.02.17
  # For a vector of angles theta, returns W, a d x d Givens rotation matrix:
  # W = Q.1,d %*% ... %*% Q.d-1,d %*% Q.1,d-1 %*% ... %*% Q.1,3 %*% Q.2,3 %*% Q.1,2 
##  if(theta < 0  || pi < theta){stop("theta must be in the interval [0,pi]")}
  d = (sqrt(8*length(theta)+1)+1)/2
  if(d - floor(d) != 0){stop("theta must have length: d(d-1)/2")}
  W = diag(d)
  index = 1
  for(j in 1:(d-1)){
    for(i in (j+1):d){
        Q.ij = givens.rotation(theta[index], d, c(i,j))
        W = Q.ij %*% W 
        index = index + 1
    }
  }
  W
}

"W2theta" = function(W)
{
  # David S. Matteson
  # 2011.06.27
  # Decompose a d by d orthogonal matrix W into the product of
  # d(d-1)/2 Givens rotation matrices. Returns theta, the d(d-1)/2 by 1
  # vector of angles, theta.
  # W = Q.1,d %*% ... %*% Q.d-1,d %*% Q.1,d-1 %*% ... %*% Q.1,3 %*% Q.2,3 %*% Q.1,2 
  if(dim(W)[1] != dim(W)[2]){stop("W must be a square matrix")}
  W = t(W) 
  d = dim(W)[1]
#  if(sum(abs(t(W)%*%W  - diag(d))) > 1e-10){stop("W must be an orthogonal matrix")}
  theta = numeric(d*(d-1)/2)
  index = 1
  for(j in 1:(d-1)){
    for(i in (j+1):d){      
        x = W[j,j]
        y = W[i,j]        
        theta.temp = atan2(y,x)    
        Q.ij = givens.rotation(theta.temp, d, c(i,j))
        W.temp = Q.ij %*% W  
        W = W.temp
        theta[index] = theta.temp
        index = index + 1
    }
  }
  theta 
}


"canonicalW" = function(W)
{
  if(dim(W)[1] != dim(W)[2]){stop("W must be a square matrix")}
  d = dim(W)[1]
#  if(sum(abs(t(W)%*%W  - diag(d))) > 1e-10){stop("W must be an orthogonal matrix")}
  W.temp = W
  W.new = matrix(0,d,d)
  for(i in 1:d){
    index = which.max(abs(W))
    row.index = index %% d #row
    row.index = ifelse(row.index == 0, d, row.index)
    col.index = ceiling(index / d) # col
    w.i = W.temp[row.index,]
    W.new[col.index,] = w.i * ifelse(w.i[col.index] < 0, -1, 1)
    W[row.index,] = 0
    W[,col.index] = 0
  }
  if(det(W.new) < 0) {W.new[d,] = -W.new[d,]}
  W.new
}

#############################################  
"latin.hc" = function(d, n.inits){   
  # DSM January 27, 2012
#  require(tgp)
   temp = lhs(n = n.inits, rect = matrix(rep(c(-pi,pi),each = d),d,2))
  t(temp)
}
