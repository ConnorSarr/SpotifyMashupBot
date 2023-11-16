import spotipy
from spotipy.oauth2 import SpotifyOAuth
import alive_progress
import easygui

import csv
import json
import os

print("About to test for Spotify auth details based on the bot information you put in the code") #prompt the user about the upcoming Spotify app test
print("If this crashes, try deleting the '.cache' file found either in this directory or the folder before it")
print("If the url says 'Invalid client' or something like it, try updating your Spotify app details")
input("Press enter to continue: ")
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="YOUR_CLIENT_ID",
                                               client_secret="YOUR_CLIENT_SECRET",
                                               redirect_uri="https://localhost/",
                                               scope="user-library-read",
                                               open_browser=True)) #setup the Spotify app

sp.playlist("7pr3Wnz3tDnttS5XBJ4ZLg", market="US") #try to get results about a dummy playlist to test the Spotify app is working

trackId = [] #will populate with track IDs from Playlist
artistDict = {} #dictionary with [songName:artistName]
bpmDict = {} #dictionary with [songName:bpmNum]
keyDict = {} #dictionary with [songName:key]
keyPairMatch = {0:"C",1:"C#",2:"D",3:"D#",4:"E",5:"F",6:"F#",7:"G",8:"G#",9:"A",10:"A#",11:"B",12:"C",13:"C#",14:"D",15:"D#",} #dictionary to combat Spotify's key number
truekeyDict = {} # "True Key" just refers to changing minor keys to major keys, dictionary formatted as [songName:forceMajorKey]
modeDict = {} #dictionary with [songName:keyMode], keyMode is what Spotify gives for determining Major or Minor keys (either 0 or 1)

jsonFolderPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'jsonData') #path to dump json data for playlists
csvFolderPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'CSVs') #path to dump csv files that are made

jsonFileName = "" #setup to make them later
csvFileName = ""

if not os.path.exists(jsonFolderPath): #make these directories if they dont exist
    os.makedirs(jsonFolderPath)

if not os.path.exists(csvFolderPath):
   os.makedirs(csvFolderPath)

playlistID = "" #Playlist ID to use, will also setup later

#function to put every result in a trackId List
def getResults(results):
    for track in results['items']: #for all tracks in the item result
        trackId.append(track['track']['id']) #get every ID and append to list

def getSpotData():
  #initalize a first push push
  results = sp.playlist_items(playlist_id=playlistID)
  getResults(results) #write the results

  while results['next']: #while another page exists
      results = sp.next(results) #set the next page
      getResults(results) #write the results, will loop back if there is another page

  print(f"{len(trackId)} track(s) found") #after we're done collecting all tracks, say how many tracks exist
  with alive_progress.alive_bar(len(trackId)) as bar:
      for idx, id in enumerate(trackId): #for every id in the trackID list
          nameRes = sp.track(id,"US") #result for the track detail (not the same as getting the BPM/key)
          trackName = nameRes['name'] #get the track name
          artistName = nameRes['artists'][0]['name'] #get the first artist name, don't care about secondary artists
          artistDict[trackName] = artistName #add it to the artist dict

          analysisRes = sp.audio_analysis(id) #setup spotify api analysis

          bpmRes = analysisRes['track']['tempo'] #BPM respond
          bpmRes = round(bpmRes) #round whatever decimal it gives
          bpmDict[trackName] = bpmRes #send to dictionary

          keyRes = analysisRes['track']['key'] 
          keyDict[trackName] = keyRes #same with key

          modeKey = analysisRes['track']['mode'] #mode of Major or Minor key
          if modeKey == 0:
              modeKey = "minor"
          elif modeKey == 1:
              modeKey = "major" #change to text (easier when analyzing data)
          modeDict[trackName] = modeKey

          if modeKey == "minor":
              tempVal = keyDict.get(trackName) + 3 #if the track is minor, raise it by 3 semitones to make the key always major
              if tempVal > 11: #if it exceeds the 11 semitone limit, wrap it back around
                  tempVal - 12
              truekeyDict[trackName] = tempVal #add this to the "true key" or strict major key section
          else:
              truekeyDict[trackName] = keyRes #add the major key to the strict major section
          bar() #update progress bar
"""
for trackName, artistName in artistDict.items():
    print(f"Track Name: {trackName}\nArtist Name: {artistName}\nKey: {keyPairMatch.get(keyDict.get(trackName))} {modeDict.get(trackName)}\nStrict Major Key: {keyPairMatch.get(truekeyDict.get(trackName))} major\nTempo: {bpmDict.get(trackName)}\n\n")
"""

def writeJSON():
  jsonData = {"trackId":trackId,"artistDict":artistDict,"bpmDict":bpmDict,"keyDict":keyDict,
              "trueKeyDict":truekeyDict,"modeDict":modeDict} #write the json data like this
  with open(jsonFileName, "w+") as jsonoutput: #open the json file we specified earlier
    json.dump(jsonData, jsonoutput) #dump the data we just formatted

def readJSON():
    with open(jsonFileName, "r") as jsonFile: #open the JSON file
        jsondata = json.load(jsonFile) #get the data from the file

    trackId = jsondata['trackId'] #specify variables to this json data
    artistDict = jsondata['artistDict']
    bpmDict = jsondata['bpmDict']
    keyDict = jsondata['keyDict']
    truekeyDict = jsondata['trueKeyDict']
    modeDict = jsondata['modeDict']

trackOne = [] #lists used to compare the two mashup songs, and to later write the csv to
trackTwo = []
bpmOne = []
bpmTwo = []
keyOne = []
keyTwo = []
scoreL = []

def calcResults():
    print("--- Calculating Mashup Ideas ---")
    mashupCounter = 0
    for trackOneName, artistOneName in artistDict.items(): #for every song in our dictionary (every track from a playlist)
        trackOneBpm = bpmDict.get(trackOneName) #get the BPM from the first track we're looking at


        """
        This process accounts for a BPM needed to go into double time
        A 60 BPM song and 120 BPM song match up perfectly
        """
        if trackOneBpm < 90:
           trackOneBpm = trackOneBpm * 2

        
        trackOneKey = truekeyDict.get(trackOneName) #get the strict major key for the first song (easier to compare)

        for trackTwoName, artistTwoName in artistDict.items(): #look at the song
            if(trackOneName == trackTwoName): #if the track is the same, skip it
                continue #skips comparison

            trackTwoBpm = bpmDict.get(trackTwoName) #same process for everything in the first song

            """
            This determines if the mashup was already found
            """
            tmpOneName = f"{trackOneName} - {artistOneName}"
            tmpTwoName = f"{trackTwoName} - {artistTwoName}"
            indices = [i for i, tmpOneName in enumerate(trackTwo)] #where does the first song show up in the second list
            dupFlag = False
            for index in indices:
                if(trackOne[index] == tmpTwoName): #if the second song is the other match, that means we have a duplicate
                    dupFlag = True
            
            if dupFlag: #skip it
                continue

            if trackTwoBpm < 90: #account for double time again
               trackTwoBpm = trackTwoBpm *2
            trackTwoKey = truekeyDict.get(trackTwoName)

            bpmDiff = abs(trackOneBpm - trackTwoBpm) #find distance between BPM
            keyDiff = abs(trackOneKey - trackTwoKey) #find distance betweeen keys

            score = float(1 - ((bpmDiff*.0136)+(keyDiff*.0566))) #give the mashup ability a score, with a single bpm weighing less than a single semitone change
            score = round(score,4) #round to 4 decimal points

            if(score > .9): #only consider the really good mashup ideas (if the score is above a .9)
              trackOne.append(tmpOneName)
              trackTwo.append(tmpTwoName)
              bpmOne.append(trackOneBpm)
              bpmTwo.append(trackTwoBpm) #append everything to a list to write to csv file

              keyOneFormat = ""
              keyOneFormat = keyPairMatch.get(keyDict.get(trackOneName))
              if(modeDict.get(trackOneName) == "minor"):
                keyOneFormat += "m"
              keyOne.append(keyOneFormat)


              keyTwoFormat = ""
              keyTwoFormat = keyPairMatch.get(keyDict.get(trackTwoName))
              if(modeDict.get(trackTwoName) == "minor"):
                keyTwoFormat += "m"
              keyTwo.append(keyTwoFormat) #format the keys to either include a "major" or "minor"

              scoreL.append(score)

def writeCSV():
    if len(trackOne) > 0: #if there are mashups to write down
        print(f"--- Calculated {len(trackOne)} decent mashups ---") #print the amount of mashups
        with open(csvFileName, mode ="w",encoding="utf-8", newline='') as csvfile:
            fields = ["Track One Name", "Track Two Name", "T1 BPM", "T2 BPM", "T1 Key", "T2 Key", "Score"]
            writer = csv.DictWriter(csvfile,fieldnames=fields)
            writer.writeheader()

            for idx,thing in enumerate(trackOne):
                writer.writerow({"Track One Name":trackOne[idx],"Track Two Name":trackTwo[idx],"T1 BPM":bpmOne[idx],"T2 BPM":bpmTwo[idx],
                                    "T1 Key":keyOne[idx],"T2 Key":keyTwo[idx],"Score":scoreL[idx]})
            
            print("--- Wrote mashups to CSV file ---")
            print("--- Find it in the CSVs folder where this program is located ---")
    else:
        print("Didn't find any good mashups. Try another playlist!")

def getPlaylistID():
    global playlistID
    playlistIDprompt = True
    while playlistIDprompt:
        tmpPlayID = input("Enter a playlist ID (found in a Spotify playlist link): ")
        try:
            playlistDetails = sp.user_playlist(user=None, market="US", playlist_id=tmpPlayID)
            print(f"\nUsing playlist: {playlistDetails['name']}")
            print(f"Made by Spotify user: {playlistDetails['owner']['display_name']}\n")
            playlistID = tmpPlayID
            makeFilenames()
            playlistIDprompt = False
        except spotipy.exceptions.SpotifyException:
            print("\nPlaylist invalid for some reason idk, try again.")

def makeFilenames():
    global playlistID
    global jsonFileName
    global csvFileName
    jsonFileName = os.path.join(jsonFolderPath, f"{playlistID} - DATA.json") #make the json File path
    csvFileName = os.path.join(csvFolderPath, f"{playlistID} - Mashup Ideas.csv") #make the csv File path


def getJSONFile():
    jsonPrompt = True
    global trackId
    global artistDict
    global bpmDict
    global keyDict
    global truekeyDict
    global modeDict
    global playlistID
    while jsonPrompt:
        jsonPath = easygui.fileopenbox(msg="Choose a JSON File",default=os.path.join(jsonFolderPath,"*"),filetypes=["*.json"])
        if(jsonPath.endswith(".json")):
            try:
                with open(jsonPath, "r") as jsonFile:
                    jsondata = json.load(jsonFile) 
                    trackId = jsondata['trackId'] #specify variables to this json data
                    artistDict = jsondata['artistDict']
                    bpmDict = jsondata['bpmDict']
                    keyDict = jsondata['keyDict']
                    truekeyDict = jsondata['trueKeyDict']
                    modeDict = jsondata['modeDict']
                    playlistID = jsonPath[-34:-12]
                    makeFilenames()
                    print("Good JSON File, moving to calculations\n")
                    jsonPrompt = False
            except:
                print("Invalid JSON file. Try again")
        else:
            print("Select a JSON File. Try again")

def main():
    print("\nThat seemed to work. Welcome to ConnorSarr's Spotify Mashup Grader!")
    promptChoice = True
    while promptChoice:
        choice = input("Would you like to enter an existing JSON file or enter a playlist ID? (Enter J or P): ")
        print()
        if(choice[:1].lower() == "j"):
            getJSONFile()
            calcResults() #run the calculation function
            writeCSV() #write the CSV results after calculations are done
            promptChoice = False
        elif(choice[:1].lower() == "p"):
            getPlaylistID()
            getSpotData() #get all the spotify playlist data
            writeJSON() #call the write JSON function
            readJSON() #call the read JSON function
            calcResults() #run the calculation function
            writeCSV() #write the CSV results after calculations are done
            promptChoice = False
        else:
            print("Enter either J or P\n")

    input("Press enter to exit: ")
main()