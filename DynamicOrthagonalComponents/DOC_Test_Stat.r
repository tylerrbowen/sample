# # 
"DOC_Test_Stat" = function(S.test, Lag.test){
#### (0,d,m) = n SUMMAND[i<j](rho[h,i,j](0)^2) + n*(n+2)*SUMMAND[k=1:m]SUMMAND[i!=j](rho[h,i,j](k)^2/(n-k))


q <- 0
SH <- S.test^2
n <- length(SH[,1])
d <- length(SH[1,])


L <- Lag.test

for(j in 1:(d-1)){
        for(i in ((j+1):d)){				
			q <- q + cor(SH[,j],SH[,i])^2
	
        }#end inner for		
    }#end outer for 
	q <- n*q
   
    for(lag in 1:L) { #int lag=1;lag<=L;lag++){		
        for(i in 1:(d)){  #=0;i<d;i++){	
            for(j in 1:(d)) { #=0;j<d;j++){			
                ans=0.0
                
                if(i!=j){      
                         
                    ans = cor(SH[1:(n-lag),i],SH[lag:(n-1),j]) # corr of the length less the lag offset by the lag					
                    q = q + n*(n+2)*(ans^2)/(n-lag)				#; //adjust by cross mean and store in out 			
                    
                }else{ 
                    #	//Do nothing				
                }# //end if-else 			
            } #//end j for	-- Finished column in 2nd matrix. Move to next one. 
        } #//end i for -- Finished with column in 1st matrix. Move to next one. 
    } #//end lag for. Finished calculations for this lag. Next lag. 
	
	q
}


	
	