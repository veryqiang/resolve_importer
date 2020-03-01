import PySimpleGUI as sg
import os
import DaVinciResolveScript as dvr
import datetime

import resolve_fun as rf

# init Resolve handles
resolve = dvr.scriptapp('Resolve')
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
mp = proj.GetMediaPool()
ms = resolve.GetMediaStorage()


def make_gui():
    sg.theme('DarkBlue9')
    sg.SetOptions(font=('default', 12))

    frame_import = [
        [sg.Text('Tags', pad=(20, 10)), sg.Checkbox('CAMERA', key='CAMERA'),
         sg.Checkbox('VFX', key='VFX'),
         sg.Checkbox('GRAPHIC', key='GRAPHIC'),
         sg.Checkbox('REF', key='REF')],
        [sg.Text('Filter', pad=(20, 10)), sg.Radio('File', "RADIO1", key='FileOnly'),
         sg.Radio('Folder', "RADIO1", key='FolderOnly'),
         sg.Radio('Both', "RADIO1", key='FolderAndFiles', default=True),
         sg.Button('Browse', pad=(30, 10), font=('Default', 15), size=(6, 1), key='Import')]]

    fram_timeline = [[sg.Checkbox('Timeline Notes', key='TIMELINENOTES', pad=(0, 10), default=False),
                      sg.Checkbox('Create Timeline', key='TIMELINE', default=True, pad=((150, 10), 10))],
                     [sg.InputText('Timeline notes...', text_color='pink', key='TNOTES', size=(48, 1),
                                   pad=(5, (5, 15)))]]

    frame_clips = [[sg.Checkbox('Clip Notes', key='CLIPNOTES', pad=(0, 10), default=False),
                    sg.Combo(values=['Orange', 'Apricot', 'Yellow', 'Lime', 'Olive', 'Green', 'Teal', 'Navy', 'Blue',
                                     'Purple', 'Violet', 'Pink', 'Tan', 'Beige', 'Brown', 'Chocolate'],
                             default_value='Blue(Default)', key='CLIPCOLOR', size=(15, 1), pad=((80, 10), 10)),
                    sg.Text('Clip Color', pad=(0, 10))],
                   [sg.InputText('Clip notes...', text_color='pink', key='CNOTES', size=(48, 1), pad=(5, (5, 15)))]]

    layout = [[sg.Frame('Import footage from folder', frame_import, font=('Default', 18), pad=(30, (15, 0)))],
              [sg.Frame('Clip options', frame_clips, font=('Default', 18), pad=(30, 10))],
              [sg.Frame('Timline options', fram_timeline, font=('Default', 18), pad=(30, 10))],
              [sg.Cancel('Exit', size=(6, 1), font=('Default', 15), pad=(30, 15))]]

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
                    rf.mp_add_source(input_path, add_files_flag, mp, ms)

                for a_clip in rf.get_cliplist_in_folder(imported_mp_folder):
                    if values['CLIPNOTES']:
                        a_clip.AddMarker(0, 'Green', folder_name, values['CNOTES'], 1)
                    if values['CLIPCOLOR'] != 'Blue(Default)':
                        a_clip.SetClipColor(values['CLIPCOLOR'])

                if values['TIMELINE']:
                    mp.SetCurrentFolder(imported_mp_folder)
                    rf.make_timeline_with_folder(imported_mp_folder, values['TNOTES'], values['TIMELINENOTES'],mp)

                sg.popup('done!')

    window.close()


if __name__ == '__main__':
    make_gui()
