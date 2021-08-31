Python 3.8.0 (v3.8.0:fa919fdf25, Oct 14 2019, 10:23:27) 
[Clang 6.0 (clang-600.0.57)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
>>> import powerfactory

app = powerfactory.GetApplication()
app.ResetCalculation()  # reset calculation

# Define Initial Simulate
def setupSimulation(comInc, comSim):
    comInc.iopt = "ins"  # select EMT or RMS
    comInc.iopt_show = 0
    comInc.iopt_adapt = 0
    comInc.dtemt = 0.1  # step size,unit ms
    comInc.tstart = -100  # start time, unit ms

    comSim.tstop = 1.5  # simulation stop time unit s


# define excute simulatin
def runSimulation(comInc, comSim):
    app.EchoOff()
    comInc.Execute()
    app.EchoOn()
    comSim.Execute()


# Declare 6 list with 0 * 100
def setupList(length=100, consPos=4):
    listA_ampl = [0] * length
    listA_phase = [0] * length

    listB_ampl = [0] * length
    listB_phase = [0] * length

    listC_ampl = [0] * length
    listC_phase = [0] * length

    # Define the amplitude and phase of fHz50 of file A to as constant
    listA_ampl[consPos] = 1
    listA_phase[consPos] = 0

    listB_ampl[consPos] = 1
    listB_phase[consPos] = 240

    listC_ampl[consPos] = 1
    listC_phase[consPos] = 120

    return listA_ampl, listA_phase, listB_ampl, listB_phase, listC_ampl, listC_phase

# set recorded variables
def addRecordedResult(elmRes, obj, param):
    if type(obj) is str:
        for elm in app.GetCalcRelevantObjects(obj):
            elmRes.AddVariable(elm, param)
    elif type(obj) is list:
        for elm in obj:
            elmRes.AddVariable(elm, param)
    else:
        elmRes.AddVariable(obj, param)


comInc = app.GetFromStudyCase('ComInc')
comSim = app.GetFromStudyCase('ComSim')
setupSimulation(comInc, comSim)

for num in list(range(0,100)):

        
    if (num + 1) == 5:
        
        listA_ampl[num] = 1
        listA_phase[num] = 0

        listB_ampl[num] = 1
        listB_phase[num] = 240

        listC_ampl[num] = 1
        listC_phase[num] = 120

    elif (num + 1) < 10 or (num + 1) % 10 == 0:
        app.ResetCalculation()  # reset calculation

        # set the amplitude and phase degree to original
        Phases = app.GetCalcRelevantObjects('*.ElmFsrc')
        ampA = Phases[0].GetAttribute('ampl_')
     
    
        # Check the original ampA
        app.PrintPlain("original Amplitude of A: " + str(ampA))
    
        listA_ampl, listA_phase, listB_ampl, listB_phase, listC_ampl, listC_phase = setupList(100, 4)
        # Set the value of file A B C
        listA_ampl[num] = 0.1
        listA_phase[num] = 0

        listB_ampl[num] = 0.1
        listB_phase[num] = 240

        listC_ampl[num] = 0.1
        listC_phase[num] = 120


        Phases[0].ampl_ = listA_ampl
        Phases[0].phase_ = listA_phase
        Phases[1].ampl_ = listB_ampl
        Phases[1].phase_ = listB_phase
        Phases[2].ampl_ = listC_ampl
        Phases[2].phase_ = listC_phase

       
        # Excute dynamic simulation
        runSimulation(comInc, comSim)
    
        # define Result file,Voltage Output Onshore to Grid
        resultFile = app.GetFromStudyCase(".ElmRes")
        resultFile.Load()
    
        V_aggregated = app.GetCalcRelevantObjects('aggregated.ElmTerm')[0]
        C_source = app.GetCalcRelevantObjects('Source.ElmVac')[0]
        AllCalculations = app.GetCalcRelevantObjects('*.ElmRes')[0]
    
        elmRes = comInc.p_resvar
    
        # export result as csv file
        comRes = app.GetFromStudyCase("ComRes")
    
        comRes.pResult = elmRes
        comRes.iopt_exp = 6  # to export as csv
        comRes.f_name = r"R:\Profile\Desktop\aggregated_new\aggregated_Voltage_Current{}.csv".format(str((num + 1) * 10))  # File Name Voltage
        comRes.iopt_sep = 1  # to use the system seperator
        comRes.iopt_honly = 0  # to export data and not only the header
        comRes.iopt_csel = 1  # export only selected variables
    
        resultObject = [None, None, None, None, None, None, None]
        elements = [AllCalculations, V_aggregated, V_aggregated, V_aggregated, C_source, C_source, C_source]
        variable = ["b:tnow", "m:U:A", "m:U:B", "m:U:C", "m:I:bus1:A", "m:I:bus1:B", "m:I:bus1:C"]
    
        comRes.resultobj = resultObject  # Export selected
        comRes.element = elements
        comRes.variable = variable
    
        comRes.Execute()
    
