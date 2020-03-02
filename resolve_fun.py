import os


def get_cliplist_in_folder(mp_folder):
    """return a list containing all clips inside folder"""
    cliplist = []
    cliplist += mp_folder.GetClips().values()
    subfolder_list = get_all_subfolders(mp_folder)
    for subfolder in subfolder_list:
        cliplist += subfolder.GetClips().values()
    return cliplist


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


def mp_add_source(fpath, add_files_flag, media_pool, media_storage):
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
            cf = media_pool.GetCurrentFolder()
            # remember handle of current mediapool root
            for dir in dirs:
                sub_temp.append(media_pool.AddSubFolder(cf, dir))
            media_pool.SetCurrentFolder(cf)
            # AddSubFolder changes currentfolder to new added, return to cf
            if add_files_flag:
                for file in files:
                    media_storage.AddItemsToMediaPool(os.path.join(root, file))
            media_pool.SetCurrentFolder(sub_temp[0])
            # change current folder to the next root folder os.walk() returns, which is sub_temp[0]
            folder_handles.extend(sub_temp)
            # store sub folders handles to the list
        if not dirs:
            # if subfolder does not exist, move on to the next folder in the folder_handles list

            # add the files  first
            if add_files_flag:
                for file in files:
                    media_storage.AddItemsToMediaPool(os.path.join(root, file))

            # if next folder exist, change to next folder
            try:
                if folder_handles[i]:
                    media_pool.SetCurrentFolder(folder_handles[i])
                    i += 1
            except IndexError:
                pass


def make_timeline_with_folder(mp_folder, notes, timeline_notes_flag, media_pool):
    """make a timeline with all files inside the 'mp_folder' object;
    Keyword Arguments:
        mp_folder - Resolve media pool folder object
    """
    mp_folder_name = mp_folder.GetName()
    # initial timeline and marker
    media_pool.SetCurrentFolder(media_pool.GetRootFolder())
    new_timeline = media_pool.CreateEmptyTimeline(mp_folder_name)
    media_pool.SetCurrentFolder(mp_folder)
    media_pool.AppendToTimeline(list(mp_folder.GetClips().values()))
    if timeline_notes_flag:
        new_timeline.AddMarker(new_timeline.GetEndFrame() - new_timeline.GetStartFrame(),
                               'Green', mp_folder_name, notes, 1)
    # work on the subfolders, add clips inside subfolder to timeline, and marker at the end
    subfolder_list = get_all_subfolders(mp_folder)
    for subfolder in subfolder_list:
        clips_in_this_subfolder = []
        for clip in subfolder.GetClips().values():
            clips_in_this_subfolder.append(clip)
        media_pool.AppendToTimeline(clips_in_this_subfolder)
        if timeline_notes_flag:
            new_timeline.AddMarker(new_timeline.GetEndFrame() - new_timeline.GetStartFrame(),
                                   'Green', subfolder.GetName(), notes, 1)
    return new_timeline


def get_newest_renderjob_index(proj):
    newest_index= max(k for k,v in proj.GetRenderJobs().items())
    return newest_index


def valid_video_track_count(timeline):
    i=0
    for track in range(1,int(timeline.GetTrackCount('video'))+1):
        if timeline.GetItemsInTrack('video', track):
            i+=1
    return i


