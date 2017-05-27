from django.shortcuts import render
import csv
from myOpt.models import OptimizationData,FinalData
from datetime import datetime,timedelta
import datetime
from django.http import HttpResponse
import xlsxwriter
from numpy.lib.function_base import average
import math
from pandas import Series
from pandas import DataFrame
from pandas import concat
from matplotlib import pyplot
import numpy as np
from pandas.core.frame import DataFrame
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.ar_model import AR
from statsmodels.tsa.arima_model import ARIMA

#Create your views here.
def readAndWriteData(request):
    OptimizationData.objects.all().delete()
    counter = 0
    csv_file = open('example.csv')
    csv_reader = csv.reader(csv_file, delimiter = ',')
    next(csv_reader)
    objList = []
    for row in csv_reader:
        s = row[0]
        d =datetime.datetime.strptime(s, '%d-%m-%Y').strftime('%Y-%m-%d')
        
        newRow = OptimizationData(date = d, store = row[1],location = row[2],code = row[3],salerProductName = row[4],mainGroup = row[5],subGroup = row[6],productVariety = row[7],salesAmount = row[8])
        objList.append(newRow)
        counter = counter + 1
        if counter % 20 == 0:
            OptimizationData.objects.bulk_create(objList)
            objList = []
       
    if objList:
         OptimizationData.objects.bulk_create(objList)
        
    csv_file.close()
    return HttpResponse('finito')
 
def readFromDB(request):
     oldopt = OptimizationData.objects.filter(productVariety = 'cesit-1').order_by('date')
     FinalData.objects.all().delete()
     count = 0
     objlist = []
     for obj in oldopt:
         if count == 0:
             lastDate = obj.date
             lastAmount = obj.salesAmount
         else:
            if lastDate == obj.date:
                obj.salesAmount = lastAmount + obj.salesAmount
                lastObj = obj
            else:
                newEntry = FinalData(date = lastObj.date,salesAmount = lastObj.salesAmount)
                objlist.append(newEntry)
                lastObj = obj
                lastDate = obj.date
                
            if len(objlist) == 20:
                FinalData.objects.bulk_create(objlist)
                objlist = []
         count+= 1   
    
     if objlist:
         FinalData.objects.bulk_create(objlist)
         
     opt = FinalData.objects.all()
     opt2 = FinalData.objects.all()
     fitCount = 0
     weeklyFit = []
     weekCount = 0
     totalCount = 0
     finalArray = []
     for obj in opt2:
             weeklyFit.append(obj)
             weekCount += 1
             totalCount += 1
             if weekCount == 7 or totalCount == 333:
                total = 0
                for objs in weeklyFit:
                    total += objs.salesAmount
                if weekCount == 7:
                    average = total/7
                else:
                    average = total/5
                for objs in weeklyFit:
                    distance = objs.salesAmount - average
                    finalArray.append(objs.salesAmount - distance/2)
                weekCount = 0
                weeklyFit = []
     fitCount2 = 0
     weeklyFit2 = []
     weekCount2 = 0
     totalCount2 = 0
     finalArray2 = []
     threefit = []
     for obj in opt2:
             weeklyFit2.append(obj)
             weekCount2 += 1
             totalCount2 += 1
             if weekCount2 == 7 or totalCount2 == 333:
                total = 0
                for objs in weeklyFit2:
                    total += objs.salesAmount
                    
                if weekCount2 == 7:
                    average = total/7
                else:
                    average = total/5
                
                fitCount2 = 0
                
                for objs in weeklyFit2:
                    fitCount2+=1
                    average2 = average
                    threefit.append(objs)
                    totalthree = 0
                    if fitCount2 == 3:
                        for objss in threefit:
                             totalthree += objss.salesAmount
                        average2 = totalthree/3
                        threefit = []
                        fitCount2 = 0
                    finalArray2.append(average2)
                weekCount2 = 0
                weeklyFit2 = []
    
     baseArray = []
     predictionArray = []
     totalAverage = 0
     total = 0
     lastMonthAverage = 0
     totalLastMonth = 0
     realArray = []
     monthCount = 0
     monthTurn = 0
     patternArray = []
     febTurn = 0
     totalBaseCount = 0
     for i in range(31):
        patternArray.append(0)
        
     for obj in opt2:
        if totalBaseCount < 258:
            total += obj.salesAmount
        if totalBaseCount < 258:
            if totalBaseCount == 0:
                patternArray[monthCount] = obj.salesAmount
            else:
                patternArray[monthCount] += obj.salesAmount
        if obj.date > datetime.date(2016,12,31) and obj.date < datetime.date(2017,2,1):
            baseArray.append(obj)
            totalLastMonth += obj.salesAmount
            monthTurn = 0
        if obj.date > datetime.date(2017,1,31) and obj.date < datetime.date(2017,3,1):
            realArray.append(obj)
            febTurn = 1    
        monthCount+= 1
        if febTurn == 1 and monthCount == 28:
            monthCount = 0
            monthTurn = 0
            febTurn = 0
        if monthTurn == 0 and monthCount == 31:
            monthCount = 0
            monthTurn = 1
        if monthTurn == 1 and monthCount == 30:
            monthCount = 0
            monthTurn = 0
        totalBaseCount+=1
     for i in range(28):
         patternArray[i] = patternArray[i]/258
     lastMonthAverage = totalLastMonth/31
     totalAverage = total/258
     predictCount = 0
     predictAverage = totalAverage + (lastMonthAverage - totalAverage)/3*4
     predictTotal = predictAverage * 28
     remaining = 0
     while predictCount < 28:
         if predictCount == 0:
             temp = (baseArray[predictCount].salesAmount/5*3 + patternArray[predictCount]/5*2) + lastMonthAverage - totalAverage
             remaining = ((baseArray[predictCount].salesAmount/5*3 + patternArray[predictCount]/5*2) - predictAverage)/4
             
         else:
             if remaining != 0:
                temp = (baseArray[predictCount].salesAmount/5*3 + patternArray[predictCount]/5*2) - remaining + lastMonthAverage - totalAverage
                remaining = ((baseArray[predictCount].salesAmount/5*3 + patternArray[predictCount]/5*2) - predictAverage)/4
             else:
                temp = (baseArray[predictCount].salesAmount/5*3 + patternArray[predictCount]/5*2) + lastMonthAverage - totalAverage
         
         temp = math.ceil(temp)
         predictionArray.append(temp)
         predictCount+=1      
     workbook = xlsxwriter.Workbook('Prediction.xlsx')
     worksheet = workbook.add_worksheet('Sheet 1')
     bold = workbook.add_format({'bold': True})
     worksheet.write('A1', 'Date', bold)
     worksheet.write('B1', 'Amount', bold)
     worksheet.write('C1', 'BasicFit', bold)
     worksheet.write('D1', 'RoundFit', bold)
     worksheet.write('E1', 'RealFeb', bold)
     worksheet.write('F1', 'PredictedFeb', bold)
     worksheet.write('H1','Date',bold)
     worksheet.write('I1','Predicted Amount',bold)
     worksheet.write('J1','Real Amount',bold)

     row = 1
     col = 0
     row2 = 1
     col2 = 7
     row3 =1
     array = []
     date  = []
     sayac = 0
     

     totalCount = 0
     for obj in opt:
        worksheet.write(row, col,str(obj.date))
        worksheet.write(row, col + 1, obj.salesAmount)
        worksheet.write(row, col + 2, finalArray[totalCount])
        worksheet.write(row, col + 3, finalArray2[totalCount])
        if totalCount<28:
            worksheet.write(row, col + 4, realArray[totalCount].salesAmount)
            worksheet.write(row, col + 5, predictionArray[totalCount])
        if sayac>=259 and sayac <= 286:
            worksheet.write(row3,col2,str(obj.date))
            row3+=1
        array.append(obj.salesAmount)
        date.append(str(obj.date))
        row += 1
        sayac+=1
        if totalCount!=333:
            totalCount+=1
# Write a total using a formula.
     X = array
     size =int( len(X) * 0.916)
     train, test, tasi= X[0:259], X[259:287],X[287:len(X)]
     train.extend(tasi)
     print ('TEST')
     print(test)
     print(train)
     history = [x for x in train]
     a =np.array(history, dtype=np.float64)
     p = a.tolist()
     myarr = []
     myarr = p
     sayac2 = 0
     predictions = list()
     for t in range(len(test)):
         sayac2+=1     
         model = ARIMA(myarr[0:len(train)-len(test)+t], order=(5,1,0))
         model_fit = model.fit(disp=False)
         output = model_fit.forecast()
         yhat = output[0]
         predictions.append(yhat)
         obs = test[t]
         history.append(obs)
         worksheet.write(row2,col2+1,yhat)
         worksheet.write(row2,col2+2,obs)
         row2+=1
     error = mean_squared_error(test, predictions)
     print('Test MSE: %.3f' % error)

     pyplot.plot(test)
     pyplot.plot(predictions, color='red')
     pyplot.show()



     chart = workbook.add_chart({'type': 'line'})


     chart.add_series({
         'values': ['Sheet 1', 0, 1,row-1 ,1],
         'categories' : ['Sheet 1', 1, 0, row-1, 0],
        'line' : {'color': 'blue'},
         'name' : 'Real Amount',
     })
     chart.add_series({
         'values': ['Sheet 1', 0, 2,row-1 ,2],
         'categories' : ['Sheet 1', 1, 0, row-1, 0],
        'line' : {'color': 'orange'},
         'name' : 'BasicFit',
     })
     chart.set_title ({'name': 'Optimization Results'})
     chart.set_x_axis({'name': 'Sales Amount'})
     chart.set_y_axis({'name': 'Date'})
     
     chart2 = workbook.add_chart({'type': 'line'})


# Configure the chart. In simplest case we add one or more data series.
     chart2.add_series({
         'values': ['Sheet 1', 0, 1,row-1 ,1],
         'categories' : ['Sheet 1', 1, 0, row-1, 0],
        'line' : {'color': 'blue'},
         'name' : 'Real Amount',
     })
     chart2.add_series({
         'values': ['Sheet 1', 0, 3,row-1 ,3],
         'categories' : ['Sheet 1', 1, 0, row-1, 0],
        'line' : {'color': 'orange'},
         'name' : 'roundFit',
     })
     chart2.set_title ({'name': 'Optimization Results2'})
     chart2.set_x_axis({'name': 'Sales Amount'})
     chart2.set_y_axis({'name': 'Date'})
     
     chart3 = workbook.add_chart({'type': 'line'})


# Configure the chart. In simplest case we add one or more data series.
     chart3.add_series({
         'values': ['Sheet 1', 0, 4,28 ,4],
         'categories' : ['Sheet 1', 260, 0, 287, 0],
        'line' : {'color': 'blue'},
         'name' : 'Real Amount',
     })
     chart3.add_series({
         'values': ['Sheet 1', 0, 5,28 ,5],
         'categories' : ['Sheet 1', 260, 0, 287, 0],
        'line' : {'color': 'orange'},
         'name' : 'roundFit',
     })
     
     chart4 = workbook.add_chart({'type': 'line'})

     chart4.add_series({ #real
        'values': ['Sheet 1', 1, 9,row2-1 ,9],
        'categories' : ['Sheet 1', 1, 7, row3-1, 7],
        'line' : {'color': 'blue'},
        'name' : 'Real Amount',
     })
     
     chart4.add_series({ #predicted
        'values': ['Sheet 1', 1, 8,row2-1 ,8],
        'categories' : ['Sheet 1', 1, 7, row3-1, 7],
        'line' : {'color': 'red'},
        'name' : 'Real Amount',
     }) 
     
     chart.set_title ({'name': 'Weekly Fit'})
     chart.set_x_axis({'name': 'Sales Amount'})
     chart.set_y_axis({'name': 'Date'})        
     
     chart2.set_title ({'name': '3 Days Fit'})
     chart2.set_x_axis({'name': 'Sales Amount'})
     chart2.set_y_axis({'name': 'Date'})   
     
     chart3.set_title ({'name': 'Optimization Results with our algorithm (For February)'})
     chart3.set_x_axis({'name': 'Sales Amount'})
     chart3.set_y_axis({'name': 'Date'})
     
     chart4.set_title ({'name': 'Regression Result with ARIMA  (For February)'})
     chart4.set_x_axis({'name': 'Sales Amount'})
     chart4.set_y_axis({'name': 'Date'})
     
     worksheet.insert_chart('L1', chart)
     worksheet.insert_chart('L16', chart2)
     worksheet.insert_chart('L30', chart3)
     worksheet.insert_chart('L45', chart4)

     workbook.close()
     return HttpResponse('readFinito')
        
