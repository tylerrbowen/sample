"doc.in.var"=function(theta_s, Z_s, L_s, PHI_s, C_s) {
    
    
    theta_r <- as.numeric(theta_s)
    theta <- theta_r
    
    Z <- as.matrix(Z_s)
    d <- as.numeric(ncol(Z_s))
    n <- as.numeric(nrow(Z_s))
    L <- as.numeric(L_s)
    
    PHI <- as.matrix(PHI_s)
    
    C_s <- as.numeric(C_s)
    
    Iden <- diag(d)
    
    k <- 0
    
    W <- matrix(NA, d, d)
    W <- diag(d)
    ##print(W)
    for(j in 1:(d-1)){
        for(i in ((j+1):d)){				
            ##print(i)
            ##print(j)
            
            Q <- matrix(NA, d, d)
            ##print(Q)
            Q <- diag(d)
            ##print(Q)
            c_f <- cos(theta[k+1])
            ##print(c_f)
            s <- sin(theta[k+1])
            ##print(s)
            Q[i,i] = c_f
            ##print(Q)
            Q[j,j] = c_f
            ##print(Q)
            Q[j,i] = -s
            ##print(Q)
            Q[i,j] = s
            ##print(W)
            W = Q %*% W
            ##print(W)
            ##print(k)
            k <- k+1		
        }#end inner for		
    }#end outer for 
    
    tW <- t(W)
    ##print(tW)
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
    
    z <- 1
    ans <- 0.0; 
    b <- (d*(d-1))/2 + L*d*(d-1)
    
    out <- as.vector(b)
    
    #//Lag 0. A total of d(d-1)/2 entries in out will be filled. i and j are column numbers. k is row number 
    for(i in 1:(d-1)){	
        
        for(j in (i+1):(d)){
            
            
            ans = 0.0 #; //next column so restart 
            ans = crossprod(SH[,i],SH[,j]) #dot(SH.col(i), SH.col(j));							
            ##print(ans)
            out[z] = ans/n - ColMeans[i]*ColMeans[j] #; //adjust by cross mean and store in out 
            #print(out[z])
            z = z+1		
            
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
