'''
Created on 5 Nov 2015

@author: wnm24546
'''
import unittest
import os

#TODO: tests for changeDataDirTrigger, changeIntegrationConfigTrigger

import Lucky
from Lucky.LuckyExceptions import BadModelStateException, IllegalArgumentException
from Lucky.DataModel import (CalibrationConfigData, MainData)
from Lucky.MainPresenter import MainPresenter
from Lucky.MPStates import State

class MainPresenterTest(unittest.TestCase):
    def setUp(self):
        self.mp = MainPresenter()
        self.projectBaseDir = "/scratch/ecl-ws/misc-ws_git/dls-i15.git"
        self.testPkgDir = os.path.join(self.projectBaseDir, "uk.ac.diamond.i15.Lucky/test/Lucky")
    
    def tearDown(self):
        self.mp = None

class StartupModeTest(MainPresenterTest):
    def runTest(self):
        #Reset the Main Presenter to be our own object.
        dM = MainData(mode=(0, 1))
        self.mp = MainPresenter(dM=dM)
        self.assertEqual(self.mp.getModeTransition(), State.EVENTS.OFFLINE, "Expected offline, got live transition")
        
        dM = MainData(mode=(1, 0))
        self.mp = MainPresenter(dM=dM)
        self.assertEqual(self.mp.getModeTransition(), State.EVENTS.LIVE, "Expected live, got offline transition")

class GetStateTest(MainPresenterTest):
    def runTest(self):
        self.assertEqual(self.mp.getSMStateName(), "OfflineSetup", "Expected OfflineSetup at startup")
        
        self.assertTrue(isinstance(self.mp.getSMState(), State), "Returned State machine state is not a state instance")
   
class DataValidRunStopStateChangesTest(MainPresenterTest):
    def runTest(self):
        #Set allDataPresent
        self.assertFalse(self.mp.dataModel.runEnabled, 'Run should be disabled by default')
        self.assertFalse(self.mp.dataModel.stopEnabled, 'Stop should be disabled by default')
         
        #Data valid: Activate run by toggling
        self.mp.dataChangeTrigger(noData=True)
        self.assertTrue(self.mp.dataModel.allDataPresent, 'All data valid: not valid.')
        self.assertTrue(self.mp.dataModel.runEnabled, 'All data valid: Run should be enabled')
        self.assertFalse(self.mp.dataModel.stopEnabled, 'All data valid: Stop should be disabled')
         
        #Press run: Activate stop, deactivate run
        self.mp.runTrigger()
        self.assertFalse(self.mp.dataModel.runEnabled, 'Run triggered: Run should be disabled')
        self.assertTrue(self.mp.dataModel.stopEnabled, 'Run triggered: Stop should be enabled')
        
        #Press stop: Activate run, deactivate stop
        self.mp.stopTrigger()
        self.assertTrue(self.mp.dataModel.runEnabled, 'Stop triggered: Run should be disabled')
        self.assertFalse(self.mp.dataModel.stopEnabled, 'Stop triggered: Stop should be enabled')
        
        #Data invalid
        self.mp.dataChangeTrigger(noData=True)
        self.assertFalse(self.mp.dataModel.allDataPresent, 'All data not valid: valid.')
        self.assertFalse(self.mp.dataModel.runEnabled, 'All data not valid: Run should be enabled')
        self.assertFalse(self.mp.dataModel.stopEnabled, 'All data not valid: Stop should be disabled')
        
class IsValidPathTest(MainPresenterTest):
    def runTest(self):
        dataDir = os.path.join(self.testPkgDir, "testData")
        uiText = os.path.join(dataDir, "CalibF1.txt")
        
        self.assertTrue(self.mp.isValidPath(uiText), "File "+uiText+" does not exist but should")
        self.assertTrue(self.mp.isValidPath(dataDir, dirPath=True), "Directory "+dataDir+" does not exist but should")
        self.assertFalse(self.mp.isValidPath(uiText+"badger"), "File "+uiText+"badger does exists but should not")
        self.assertFalse(self.mp.isValidPath(dataDir), "Directory "+dataDir+" is a file")
        
    
class IsValidNumberTest(MainPresenterTest):
    def runTest(self):
        intTestValue = 900
        floatTestValue = 15.5
        notANumberValue = "Fish"
        
        self.assertTrue(self.mp.isValidNumber(intTestValue), str(intTestValue)+" is not a number")
        self.assertTrue(self.mp.isValidNumber(floatTestValue), str(floatTestValue)+" is not a number")
        self.assertFalse(self.mp.isValidNumber(notANumberValue), str(notANumberValue)+"is a number")
    
class ModeSettingTest(MainPresenterTest):
    def runTest(self):
        self.assertEqual(self.mp.getSMStateName(), "OfflineSetup", "Expected OfflineSetup at startup")
        
        #Set to live setup
        uiData = (1, 0)
        self.mp.setModeTrigger(uiData)
        self.assertEqual(self.mp.getSMStateName(), "LiveSetup")
        
        #Set to offline setup
        uiData = (0, 1)
        self.mp.setModeTrigger(uiData)
        self.assertEqual(self.mp.getSMStateName(), "OfflineSetup")
        
        with self.assertRaises(BadModelStateException):
            uiData = (1, 1)
            self.mp.setModeTrigger(uiData)
            #Invalid mode setting accepted
        
class CalibrationTypeSettingTest(MainPresenterTest):
    def runTest(self):
        uiData = (1, 0, 0)
        self.assertEqual(self.mp.dataModel.calibType, uiData, "Incorrect setting: expecting "+str(uiData))
        
        uiData = (0, 1, 0)
        self.mp.setCalibTypeTrigger(uiData)
        self.assertEqual(self.mp.dataModel.calibType, uiData, "Incorrect setting: expecting "+str(uiData))
        
        uiData = (0, 0, 1)
        self.mp.setCalibTypeTrigger(uiData)
        self.assertEqual(self.mp.dataModel.calibType, uiData, "Incorrect setting: expecting "+str(uiData))
        
        uiData = (1, 0, 0)
        self.mp.setCalibTypeTrigger(uiData)
        self.assertEqual(self.mp.dataModel.calibType, uiData, "Incorrect setting: expecting "+str(uiData))
        
        with self.assertRaises(BadModelStateException):
            uiData = (1, 1, 0)
            self.mp.setCalibTypeTrigger(uiData)
            #Calibration selection should be invalid

class ChangeDataDirTest(MainPresenterTest):
    def runTest(self):
        dataDir = os.path.join(self.testPkgDir, "testData")
        self.assertTrue(self.mp.changeDataDirTrigger(dataDir), "Data dir should be valid")
        self.assertEqual(self.mp.dataModel.dataDir, dataDir, "Data dir has not been updated")
        
#         currUSDSPairTab = self.mp.dataModel.usdsPairTable
#         self.assertEqual(len(currUSDSPairTab), 1, "US/DS pair table not correctly updated")
#         self.assertEqual(len(currUSDSPairTab[0]), 2, "US/DS pair table has wrong structure")
#         self.assertEqual(currUSDSPairTab[0][0], "T_635_1.txt", "US/DS pair table incorrectly populated")

class USDSPairSelectionTest(MainPresenterTest):
    def runTest(self):
        with self.assertRaises(IllegalArgumentException):
            self.mp.changeUSDSPairTrigger()
        
        with self.assertRaises(IllegalArgumentException):
            self.mp.changeUSDSPairTrigger(inc=True, pairNr=14)
        
        self.assertTrue(self.mp.changeUSDSPairTrigger(pairNr=12), "Failed to change USDS pair to 12")
        self.assertEqual(self.mp.dataModel.usdsPair, 12, "US/DS pair has not updated")
        self.assertFalse(self.mp.changeUSDSPairTrigger(pairNr=-34), "Negative number for pair index accepted")
        self.assertEqual(self.mp.dataModel.usdsPair, 12, "US/DS pair has updated")
        
        self.mp.dataModel.usdsPair = 0
        
        self.assertFalse(self.mp.changeUSDSPairTrigger(dec=True), "US/DS pair decremented to negative number")
        self.assertEqual(self.mp.dataModel.usdsPair, 0, "US/DS pair has updated")
        self.assertTrue(self.mp.changeUSDSPairTrigger(inc=True), "US/DS pair has not incremented")
        self.assertEqual(self.mp.dataModel.usdsPair, 1, "US/DS pair has not updated")
        self.assertTrue(self.mp.changeUSDSPairTrigger(dec=True), "US/DS pair has not decremented")
        self.assertEqual(self.mp.dataModel.usdsPair, 0, "US/DS pair has not updated")
        
        #Add tests for multiple inputs

class ChangeIntegrationConfigTest(MainPresenterTest):
    def runTest(self):
        integSetup = [300, 800, 100]
        uiData = integSetup
        self.assertEqual(self.mp.changeIntegrationConfigTrigger(uiData), [True, True, True], "Integration config should be valid")
        self.assertEqual(self.mp.dataModel.integrationConf, integSetup, "Integration config has not been updated")
        
        integSetup = [300, 100, 200]
        self.mp.assertEqual(self.mp.changeIntegrationConfigTrigger(uiData), [True, False, True], "Integration config should not be valid")
        self.assertNotEqual(self.mp.dataModel.integrationConf, integSetup, "Integration config has been updated")
        
        integSetup = [300, 800, -10]
        self.mp.assertEqual(self.mp.changeIntegrationConfigTrigger(uiData), [True, True, False], "Integration config should not be valid")
        self.assertEqual(self.mp.dataModel.integrationConf, integSetup, "Integration config has been updated")

class CalibrationConfigUpdateTest(MainPresenterTest):
    def runTest(self):
        #Create new CCData object; pass to method; check mp values are now updated
        pass
    
    
    
    
    class RunPressedAllUIChangesTest(MainPresenterTest):
        pass
#     def runTest(self):
#         self.mp.dataModel.allDataPresent = True
#         self.mp.toggleButtonStates()
#         
#         #This is for offline-mode
#         ####
#         #Fake starting a run
#         self.mp.doRun(test=True)
#         self.assertFalse(self.mp.dataModel.allUIControlsEnabled, 'UI controls should be disabled after start')
#         self.assertFalse(self.mp.dataModel.runEnabled, 'Run should be disabled after start')
#         self.assertTrue(self.mp.dataModel.stopEnabled, 'Stop should be enabled after start')
#         self.assertFalse(self.mp.dataModel.usdsControlsEnabled, 'US/DS pair selector should be disabled during run')
#         
#         #Fake stopping a run
#         self.mp.doStop(test=True)
#         self.assertTrue(self.mp.dataModel.allUIControlsEnabled, 'UI controls should be enabled after stop')
#         self.assertTrue(self.mp.dataModel.runEnabled, 'Run should be enabled after stop')
#         self.assertFalse(self.mp.dataModel.stopEnabled, 'Stop should be disabled after stop')
#         self.assertTrue(self.mp.dataModel.usdsControlsEnabled, 'US/DS pair selector should be enabled after stop')
# 
#         #This is for live-mode
#         ####
#         self.mp.setMode()#TODO This needs thought
#         self.mp.doRun(test=True)
#         self.assertFalse(self.mp.dataModel.usdsControlsEnabled, 'US/DS pair selector should be disabled in live-mode')
#         
#         self.mp.doStop(test=True)
#         self.assertFalse(self.mp.dataModel.usdsControlsEnabled, 'US/DS pair selector should be disabled in live-mode')
        