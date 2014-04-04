#library(prob)
#Photo Estabilish directors for matching Dropbox
#inputdir <- "C:/Users/photo/Dropbox/Robert/Work/Org-3.0"

#Air Estabilish directors for matching Dropbox
inputdir<-"/Users/bobrunning2004/Dropbox/Robert/Work/Org-3.0"

#Ubuntu Estabilish directors for matching Dropbox
inputdir <- "/home/bob/Dropbox/Robert/Work/Network Reliability/Simulation Cell Failure"


#Work Estabilish directors for matching Dropbox
inputdir <- "C:/Documents and Settings/RJakubek/My Documents/Dropbox/Robert/Work/Network Reliability/Simulation Cell Failure"

setwd(inputdir);


x<-rbinom(n=1:10000000, size=1, prob=0.99999)

#Challenge is 5 9s is 5 minutes of outage per year, I would need to do the analysis on a minute basis or525,600 times for one year
# I would also need to capture maintenanc times, 4 hours MTTR, because that now plays into the failure




" Key points - 
Reliability topology may be very differnt than physical topoloy
It is up to the analyst to construct the reliability topology, or reliability block diagram
The level of detail in the reliability block diagram is determined by the objective of the analysis
 p is the probability an event will occur
 q is the probability an event will not occur

We need to estabilish a criteria for system failure.This requres knowledge of the physical topology
and it request the understanding of the relability topology.

note two RRUs need to fail for customer outage, RET controlloer cost money but don't create outages

The reliability of serial items is the multiplication of the reliability rate
The reliability of parallel items is the one minus the muliptilicaiton of the failure rate

"


SimpleSim <- function(..., fun, pairwise=F) {
  # SimpleSim allows for the calling of a function varying 
  
  # multiple parameters entered as vectors. In pairwise form 
  
  # it acts much like apply. In non-paiwise form it makes a 
  
  # combination of each possible parameter mix
  
  # in a manner identical to block of nested loops.
  
  returner <- NULL
  L        <- list(...)
  # Construct a vector that holds the lengths of each object
  vlength <- unlist(lapply(L, length)) 
  npar    <- length(vlength)
  CL      <- lapply(L, "[", 1) # Current list is equal to the first element
  
  # Pairwise looping
  if (pairwise) {
    # If pairwise is selected than all elements greater than 1 must be equal.
    # Checks if all of the elements of a vector are equal
    if (!(function(x) all(x[1]==x))(vlength[vlength>1])) {
      print(unlist(lapply(L, length)))
      stop("Pairwise: all input vectors must be of equal length", call. =F)
    }
    for (i in 1:max(vlength)) { # Loop through calling the function
      CL[vlength>1]  <- lapply(L, "[", i)[vlength>1] # Current list
      returner <- rbind(returner,c(do.call(fun, CL),pars="", CL))
    }
  } # End Pairwise
  
  # Non-pairwise looping
  if (!pairwise) {
    ncomb <- prod(vlength) # Calculate the number of combinations
    print(paste(ncomb, "combinations to loop through"))
    comb <- matrix(NA, nrow=prod(vlength), ncol=npar+1)
    comb[,1] <- 1:prod(vlength) # Create an index value
    comb <- as.data.frame(comb) # Converto to data.frame
    colnames(comb) <- c("ID", names(CL))
    for (i in (npar:1)) { # Construct a matrix of parameter combinations
      comb[,i+1] <- L[[i]] # Replace one column with values
      comb<-comb[order(comb[,(i+1)]),] # Reorder rows
    }
    comb<-comb[order(comb[,1]),]
    for (i in 1:ncomb) {
      for (ii in 1:npar) CL[ii] <- comb[i,ii+1]
      returner <- rbind(returner,c(do.call(fun, CL),pars="", CL))
    }
  } # End Non-Pairwise
  
  return(returner)
  
} # END FUNCTION DEFINITION

# Let's first define a simple function for demonstration
minmax <- function(...) c(min=min(...),max=max(...))

# Pairwise acts similar to that of a multidimensional apply across columns 
SimpleSim(a=1:20,b=-1:-20,c=21:40, e=41:60,pairwise=F, fun="minmax")
# The first set of columns are those of returns from the function "fun" called.
# The second set divided by "par" are the parameters fed into the function.
SimpleSim(a=1:20,b=-1:-20,c=10, pairwise=T, fun="minmax")

# Non-pairwise creates combinations of parameter sets.
# This form is much more resource demanding.
SimpleSim(a=1:5,b=-1:-5,c=1:2, pairwise=F, fun="minmax")


celllist <-read.csv("celllist2013.csv",header = T,skip = 0, na.strings="", dec =".")
cell<-celllist[celllist$Reg == "CN" & celllist$St. == "A" & celllist$Type == "CE" & celllist$State != "MN" ,
                   c("SiteNum","Market","Latitude","Longitude","State","City")]
cells<-droplevels(cell)

ret <- .900
antenna<-.990
rru <- .999
enodeb<-.9999
metroe<-.90
metroe2<-.90
metroe3<-.90
aggrouter<-.9999

failurerates<-as.data.frame(cbind(cells = cell$SiteNum,ret,antenna,rru,enodeb,metroe,metroe2,metroe3,aggrouter))


pericsson<- .89 #percent Ericsson 70%
pnsn<-.11 # percent NSN 30%
rericssonrru<- 1-.991 #reliability of RRUs
rnsnrru<-1-.999 #reliability of RRUs
nrru<-6 # number of RRUs per cell site
ncell<-1702 #number of cell sites
annualfailrate<-0 #annual failure rate
annualfailrate<- ((rericssonrru * pericsson) + (rnsnrru * pnsn))
print(annualfailrate)
failures<- annualfailrate * ncell * nrru
print(failures)

x<- .8 * .3
y<- x/.87
print(y)


#conditional probability is p(E and F)/P(F) 

