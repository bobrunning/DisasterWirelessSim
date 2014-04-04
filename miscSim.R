library("MASS")
x<-rbeta(n = 30000,4,1)
h<-hist(x,breaks = 10,plot=FALSE)
h$counts=h$counts/sum(h$counts)
plot(h)

x <- seq(0, 1, length = 21)
hist(dbeta(x, 5, 10))
hist(pbeta(x, 5, 1))


h <- hist(vec, breaks = 100, plot=FALSE)
