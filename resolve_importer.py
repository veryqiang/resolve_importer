import PySimpleGUI as sg
import os
import DaVinciResolveScript as dvr
import datetime

resolve=dvr.scriptapp('Resolve')
pm=resolve.GetProjectManager()
proj=pm.GetCurrentProject()
mp=proj.GetMediaPool()
ms=resolve.GetMediaStorage()



def mp_add_VFX(fname, fpath,  afiles):
    print(fpath)
    folder_handles=[]
    i=1
    # mp.GetCurrentFolder()
    for root, dirs, files in os.walk(fpath):
        # print(root, dirs, files)
        #if subfolder dir exists under current root
        if dirs:
            sub_temp=[]
            #remember handle of current mediapool root
            cf = mp.GetCurrentFolder()
            #add dir to current mediapool root
            for dir in dirs:
                sub_temp.append(mp.AddSubFolder(cf, dir))
            #AddSubFolder changes currentfolder to new added, return to cf
            mp.SetCurrentFolder(cf)
            #if add file is enabled, add files
            if afiles:
                for file in files:
                    fileadded = ms.AddItemsToMediaPool(os.path.join(root, file))
                    print("Added file:", file)
            #change current folder to the first subfolder
            mp.SetCurrentFolder(sub_temp[0])
            #store sub folders to the "big" folder walk list
            folder_handles.extend(sub_temp)
        #if subfolder does not exist, move on to the next folder in the big walk list
        if not dirs:
            #add the files  first
            if afiles:
                for file in files:
                    fileadded = ms.AddItemsToMediaPool(os.path.join(root, file))
                    print("Added file:", file)
            #if next folder exist, change to next folder
            if folder_handles[i]:
                mp.SetCurrentFolder(folder_handles[i])
                i+=1


# Layout the design of the GUI

layout = [[sg.Text('Import footage from folder', font=('Default', 15), pad=(20,10)),
           sg.Button('Browse', pad=(40,10), font=('Default', 15), size=(6,1),key='Import')],
          [sg.Text('Tags', pad=(20,10)), sg.Checkbox('CAMERA', key='CAMERA'),
           sg.Checkbox('VFX', key='VFX'),
           sg.Checkbox('GRAPHIC', key='GRAPHIC'),
           sg.Checkbox('REF',key='REF')],
          [sg.Text('Filter', pad=(20,10)), sg.Radio('File', "RADIO1", key='FileOnly'),
           sg.Radio('Folder', "RADIO1",key='FolderOnly'),
           sg.Radio('Both', "RADIO1", key='FolderAndFiles',default=True)],
          [sg.Cancel('Exit',font=('Default', 12),pad=(20,15))]]

# Show the Window to the user
window = sg.Window('Resolve Import v0.1a', layout)

while True:
    # read pysimplegui window, init path to empty
    event, values = window.read()
    input_path = ''
    tags =('CAMERA','VFX','GRAPHIC','REF')
    #if user clicks Exit
    if event in ('Exit', None):
        break

    # if user clicks VFX import
    elif event == "Import" :
        input_path= sg.popup_get_folder('Footage path',font=("Helvetica", 16))
        #if got input path from user, add a folder, with root folder name and datetime
        if input_path:
            print(values)
            checked_tags = [key for key, val in values.items() if (val and (key in tags))]
            if not checked_tags:
                checked_tags=['untagged']
            folder_name = f"{datetime.datetime.now():%Y%m%d_%H%M%S_}"+'_'.join(checked_tags) +'-'+os.path.split(input_path)[1]
            mp.AddSubFolder(mp.GetRootFolder(), folder_name)
            #if user wants to import files only
            if values['FileOnly']:
                ms.AddItemsToMediaPool(input_path)
            else:
                if values['FolderOnly']:
                    add_file_flag=0
                else:
                    add_file_flag=1
                mp_add_VFX(folder_name, input_path, add_file_flag)
            sg.popup('done!')




window.close()
