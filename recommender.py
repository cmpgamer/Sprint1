import codecs 
from math import sqrt

class recommender:

    def __init__(self, k=1, n=5):
        self.k = k
        self.n = n
        self.data = {}
        self.username2id = {}
        self.userid2name = {}
        self.productid2name = {}
        self.cardinality = {}
        self.slopeOneDeviations = {}
        #Grab a bunch of info from the CSV
        self.artists = {}
        self.users = {}
        self.normalizedData = {}
        self.similarity = {}
        self.frequencies = {}
        self.deviations = {}
        # for some reason I want to save the name of the metric
        
        
    
    def convertProductID2name(self, id):
        if id in self.productid2name:
            return self.productid2name[id]
        else:
            return id
    
    
    def userRatings(self, id, n):
        """Return n top ratings for user with id"""
        print ("Ratings for " + self.userid2name[id])
        ratings = self.data[id]
        print(len(ratings))
        ratings = list(ratings.items())[:n]
        ratings = [(self.convertProductID2name(k), v) for (k, v) in ratings]
        # finally sort and return
        ratings.sort(key=lambda artistTuple: artistTuple[1], reverse = True)      
        for rating in ratings:
            print("%s\t%i" % (rating[0], rating[1]))
    
    
    def showUserTopItems(self, user, n):
        """ show top n items for user"""
        items = list(self.data[user].items())
        items.sort(key=lambda itemTuple: itemTuple[1], reverse=True)
        for i in range(n):
            print("%s\t%i" % (self.convertProductID2name(items[i][0]),items[i][1]))
    
    def computeDeviations(self):
        # for each person in the data:
        #    get their ratings
        for ratings in self.data.values():
            # for each item & rating in that set of ratings:
            for (item, rating) in ratings.items():
                self.frequencies.setdefault(item, {})
                self.deviations.setdefault(item, {})                    
                # for each item2 & rating2 in that set of ratings:
                for (item2, rating2) in ratings.items():
                    if item != item2:
                        # add the difference between the ratings to our
                        # computation
                        self.frequencies[item].setdefault(item2, 0)
                        self.deviations[item].setdefault(item2, 0.0)
                        self.frequencies[item][item2] += 1
                        self.deviations[item][item2] += rating - rating2
            
        for (item, ratings) in self.deviations.items():
            for item2 in ratings:
                ratings[item2] /= self.frequencies[item][item2]
    
    def pearson(self, rating1, rating2):
        sum_xy = 0
        sum_x = 0
        sum_y = 0
        sum_x2 = 0
        sum_y2 = 0
        n = 0
        for key in rating1:
            if key in rating2:
                n += 1
                x = rating1[key]
                y = rating2[key]
                sum_xy += x * y
                sum_x += x
                sum_y += y
                sum_x2 += pow(x, 2)
                sum_y2 += pow(y, 2)
        if n == 0:
            return 0
        # now compute denominator
        denominator = sqrt(sum_x2 - pow(sum_x, 2) / n) * sqrt(sum_y2 - pow(sum_y, 2) / n)
        if denominator == 0:
            return 0
        else:
            return (sum_xy - (sum_x * sum_y) / n) / denominator
    
    
    def computeNearestNeighbor(self, username):
    
        distances = []
        for instance in self.data:
            if instance != username:
                distance = self.manhattan(self.data[username], self.data[instance]) 
                distances.append((instance, distance))
                # sort based on distance -- closest first
        distances.sort(key=lambda artistTuple: artistTuple[1], reverse=True)
        return distances
    
    def recommend(self, user):
        print("we got here")
        """Give list of recommendations"""
        recommendations = {}
        # first get list of users  ordered by nearness
        nearest = self.computeNearestNeighbor(user)
        #
        # now get the ratings for the user
        #
        userRatings = self.data[user]
        #
        # determine the total distance
        totalDistance = 0.0
        for i in range(self.k):
            totalDistance += nearest[i][1]
        # now iterate through the k nearest neighbors
        # accumulating their ratings
        for i in range(self.k):
            # compute slice of pie 
            weight = nearest[i][1] / totalDistance
            # get the name of the person
            name = nearest[i][0]
            # get the ratings for this person
            neighborRatings = self.data[name]
            # get the name of the person
            # now find bands neighbor rated that user didn't
            for artist in neighborRatings:
                if not artist in userRatings:
                    if artist not in recommendations:
                        recommendations[artist] = neighborRatings[artist] *  weight
                    else:
                        recommendations[artist] = recommendations[artist] +  neighborRatings[artist] *  weight
        # now make list from dictionary and only get the first n items
        recommendations = list(recommendations.items())[:self.n]
        recommendations = [(self.convertProductID2name(k), v) for (k, v) in recommendations]
        # finally sort and return
        recommendations.sort(key=lambda artistTuple: artistTuple[1], reverse = True)
        return recommendations
    
    def manhattan(self, rating1, rating2):
        """Computes the Manhattan distance. Both rating1 and rating2 are dictionaries
           of the form {'The Strokes': 3.0, 'Slightly Stoopid': 2.5}"""
        distance = 0
        commonRatings = False 
        for key in rating1:
            if key in rating2:
                distance += abs(rating1[key] - rating2[key])
                commonRatings = True
        if commonRatings:
            return distance
        else:
            return -1 #Indicates no ratings in common
    
    def euclidean(self, rating1, rating2):
        """Computes the euclidean distance. Both rating1 and rating2 are dictionaries
           of the form {'The Strokes': 3.0, 'Slightly Stoopid': 2.5}"""
        totalDistance = 0
        distance = 0
        commonRatings = False 
        for key in rating1:
            if key in rating2:
                distance = abs(rating1[key] - rating2[key])
                totalDistance += pow(distance, 2)
                commonRatings = True
        if commonRatings:
            return pow(totalDistance, .5)
        else:
            return -1 #Indicates no ratings in common    
            
    
    def computeCosineSimilarity(self):
        averages = {}
        similarity = {}
        #We need the averages for each user for the numerator
        for userItem, ratings in self.data.items():
            userAvg = sum(ratings.values())/len(ratings)
            averages[userItem] = userAvg
        
        for user, value in self.data.items():    
            #time to do the denominator
            for band1 in value:
                newTuple = {}
                for band2 in value:
                    numerator = 0
                    denominator1 = 0
                    denominator2 = 0
                    if band1 is band2:
                        continue
                    for userItem, ratings in self.data.items():
                        if band1 in ratings and band2 in ratings:
                            userAvg = averages[userItem]
                            numerator += (ratings[band1] - userAvg) * (ratings[band2] - userAvg)
                            denominator1 += (ratings[band1] - userAvg)**2
                            denominator2 += (ratings[band2] - userAvg)**2
                    
                    finalD = (sqrt(denominator1) * sqrt(denominator2))
                    try:
                        newTuple[band2] = numerator/(sqrt(denominator1) * sqrt(denominator2)) 
                    except:
                        newTuple[band2] = 0
                similarity[band1] = newTuple
                self.similarity = similarity
        #print(similarity)
        
    def normalizeData(self, minNum, maxNum):
        normalized = {}
        listOfUsers = self.data.items()
        for userItem, ratings in listOfUsers:
            newTuple = {}
            for band in self.data:
                if band in ratings:
                    normalRate = (2*(ratings[band] - minNum) - (maxNum - minNum))/(maxNum - minNum)
                    newTuple[band] = normalRate     
            normalized[userItem] = newTuple
        self.normalizedData = normalized
        #print(normalized)
    
        
    def recommendCosine(self, minNum, maxNum):
        normalized = self.normalizedData
        similarity = self.similarity
             
        finalRatings = {}
        for user, userRatings in normalized.items():
            finalRatings[user] = {}
            for artist in self.data:
                if not artist in userRatings:
                    numerator = 0
                    denominator = 0
                    for otherArtist in self.data:
                        if otherArtist in userRatings:
                            numerator += (userRatings[otherArtist] * similarity[artist][otherArtist])
                            denominator += abs(similarity[artist][otherArtist])
                    finalRatings[user][artist] = .5*((numerator/denominator)+ 1)*(maxNum-minNum)+minNum
        print(finalRatings)  