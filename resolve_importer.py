import PySimpleGUI as sg
import os
import DaVinciResolveScript as dvr
import datetime

# init Resolve handles
resolve = dvr.scriptapp('Resolve')
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
mp = proj.GetMediaPool()
ms = resolve.GetMediaStorage()


def mp_add_source(fpath, add_files_flag):
    """add source clips to resolve's root folder;
    Keyword Arguments:
        fpath - footage folder path in OS
        add_files_flag - if True,add folders and files;Fasle, add folder structure only;
    """
    folder_handles = []
    i = 1

    for root, dirs, files in os.walk(fpath):
        # walk the folders
        if dirs:
            sub_temp = []
            cf = mp.GetCurrentFolder()
            # remember handle of current mediapool root
            for dir in dirs:
                sub_temp.append(mp.AddSubFolder(cf, dir))
            mp.SetCurrentFolder(cf)
            # AddSubFolder changes currentfolder to new added, return to cf
            if add_files_flag:
                for file in files:
                    ms.AddItemsToMediaPool(os.path.join(root, file))
            mp.SetCurrentFolder(sub_temp[0])
            # change current folder to the next root folder os.walk() returns, which is sub_temp[0]
            folder_handles.extend(sub_temp)
            # store sub folders handles to the list
        if not dirs:
            # if subfolder does not exist, move on to the next folder in the folder_handles list

            # add the files  first
            if add_files_flag:
                for file in files:
                    ms.AddItemsToMediaPool(os.path.join(root, file))

            # if next folder exist, change to next folder
            try:
                if folder_handles[i]:
                    mp.SetCurrentFolder(folder_handles[i])
                    i += 1
            except IndexError:
                pass


def get_all_subfolders(mp_folder):
    """return a list of all subfolders objects inside the provided folder object.
    Keyword Arguments:
        mp_folder - Resolve media pool folder object
    """
    folderlist = []
    folderlist += mp_folder.GetSubFolders().values()
    for sub_folder in mp_folder.GetSubFolders().values():
        folderlist += get_all_subfolders(sub_folder)
    return folderlist


def make_timeline_with_folder(mp_folder, notes):
    """make a timeline with all files inside the 'mp_folder' object;
    Keyword Arguments:
        mp_folder - Resolve media pool folder object
    """
    mp_folder_name = mp_folder.GetName()
    # initial timeline and marker
    new_timeline = mp.CreateTimelineFromClips(mp_folder_name, list(mp_folder.GetClips().values()))
    new_timeline.AddMarker(new_timeline.GetEndFrame() - new_timeline.GetStartFrame(),
                           'Green', mp_folder_name, notes, 1)
    # work on the subfolders, add clips inside subfolder to timeline, and maker at the end
    subfolder_list = get_all_subfolders(mp_folder)
    for subfolder in subfolder_list:
        clips_in_this_subfolder = []
        for clip in subfolder.GetClips().values():
            clips_in_this_subfolder.append(clip)
        mp.AppendToTimeline(clips_in_this_subfolder)
        new_timeline.AddMarker(new_timeline.GetEndFrame() - new_timeline.GetStartFrame(),
                               'Green', subfolder.GetName(), notes, 1)

# TODO GUI need some design
layout = [[sg.Text('Import footage from folder', font=('Default', 16), pad=(20, 10)),
           sg.Button('Browse', pad=(40, 10), font=('Default', 15), size=(6, 1), key='Import')],
          [sg.Text('Tags', pad=(20, 10)), sg.Checkbox('CAMERA', key='CAMERA'),
           sg.Checkbox('VFX', key='VFX'),
           sg.Checkbox('GRAPHIC', key='GRAPHIC'),
           sg.Checkbox('REF', key='REF')],
          [sg.Text('Filter', pad=(20, 10)), sg.Radio('File', "RADIO1", key='FileOnly'),
           sg.Radio('Folder', "RADIO1", key='FolderOnly'),
           sg.Radio('Both', "RADIO1", key='FolderAndFiles', default=True)],
          [sg.Checkbox('Timeline', key='TIMELINE', pad=(20, 10), default=True),
           sg.Multiline('Input notes...',key='NOTES', size=(36,1), focus=True)],
          [sg.Cancel('Exit', font=('Default', 12), pad=(20, 15))]]

window = sg.Window('Resolve Import v0.2a', layout)

while True:
    # read PySimpleGUI window
    event, values = window.read()
    input_path = ''
    tags = ('CAMERA', 'VFX', 'GRAPHIC', 'REF')

    # if user clicks Exit
    if event in ('Exit', None):
        break

    # if user clicks Browse
    elif event == "Import":
        input_path = sg.popup_get_folder('Footage path', font=("Helvetica", 16))
        if input_path:
            # assemble the tags
            checked_tags = [key for key, val in values.items() if (val and (key in tags))]
            if not checked_tags:
                checked_tags = ['untagged']
            # add the very first folder in media pool
            folder_name = f"{datetime.datetime.now():%Y%m%d_%H%M%S_}" + '_'.join(checked_tags) + '-' + \
                          os.path.split(input_path)[1]
            imported_mp_folder = mp.AddSubFolder(mp.GetRootFolder(), folder_name)
            # no folder structure
            if values['FileOnly']:
                ms.AddItemsToMediaPool(input_path)
            else:
                if values['FolderOnly']:
                    add_files_flag = 0
                else:
                    add_files_flag = 1
                mp_add_source(input_path, add_files_flag)

            if values['TIMELINE']:
                mp.SetCurrentFolder(imported_mp_folder)
                make_timeline_with_folder(imported_mp_folder, values['NOTES'])

            sg.popup('done!')

window.close()
