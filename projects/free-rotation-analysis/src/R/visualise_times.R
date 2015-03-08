library("ggplot2")
library("dplyr")
library("survival")
library("randomForest")
library("party")

rot_times = read.csv("../../data/rotation_times.csv", stringsAsFactors = FALSE)
rot_times$date <- as.Date(rot_times$date)
rot_times$weeks = as.numeric(rot_times$weeks)
head(rot_times)





ggplot(rot_times %>% filter(event == 1)) + geom_density(aes(x = weeks, group = season, fill = season))



mod <- coxph(Surv(weeks, event = event) ~ season +  cluster(Champion), data = rot_times)
summary(mod)

rf <- randomForest(factor(event) ~ weeks, data = rot_times, do.trace = TRUE)
plot(rf)


ct <- ctree(factor(event) ~ weeks, data = rot_times)
plot(ct)


rot_times$pred <- sapply(predict(ct, type = "prob"), function(x) x[2])
rot_times$pred2 <- predict(rf, type = "prob")[, 2]


dates = unique(rot_times$date)
date1 = dates[60]
head(rot_times %>% filter(date == date1) %>% arrange(-pred), 20)



## Evaluate how good prediction is
rot_times %>% group_by(date) %>% arrange(-weeks) %>% summarise(hits = sum(event[1:10]), season = unique(season))
