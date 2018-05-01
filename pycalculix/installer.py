
import glob
import os
import re
import shutil
import shlex
import subprocess
import sys
from urllib.parse import urlparse
from urllib.parse import ParseResult
import zipfile
from distutils.dir_util import copy_tree

from sys import platform as platform

import requests

def printos(os, bits):
    """Prints the operating system and bit size"""
    print('Detected {} {} bit'.format(os, bits))

def add():
    """Installs the fea tools on windows/mac/linux"""
    osname = None
    is_64bit = sys.maxsize > 2**32
    bitsize_dict = {True: 64, False: 32}
    bitsize = bitsize_dict[is_64bit]
    if platform == "linux" or platform == "linux2":
        printos('Linux', bitsize)
        ubuntu_add()
    elif platform == "darwin":
        printos('Mac OS X', bitsize)
        mac_add()
    elif platform == "win32":
        printos('Windows', bitsize)
        windows_add(bitsize)
    elif platform == "win64":
        printos('Windows', bitsize)
        windows_add(bitsize)
    print('Done!')

def remove():
    """Removes the fea tools on windows/mac/linux"""
    osname = None
    is_64bit = sys.maxsize > 2**32
    bitsize_dict = {True: 64, False: 32}
    bitsize = bitsize_dict[is_64bit]
    if platform == "linux" or platform == "linux2":
        printos('Linux', bitsize)
        ubuntu_remove()
    elif platform == "darwin":
        printos('Mac OS X', bitsize)
        mac_remove()
    elif platform == "win32":
        printos('Windows', bitsize)
        windows_remove(bitsize)
    elif platform == "win64":
        printos('Windows', bitsize)
        windows_remove(bitsize)
    print('Done!')

def ubuntu_add():
    """Adds programs on ubunut, uses apt"""
    gmsh_installed = shutil.which('gmsh')
    if not gmsh_installed:
        print('Installing gmsh')
        command_line = "sudo apt-get install gmsh.rb"
        subprocess.check_call(command_line, shell=True)
    else:
        print('gmsh present')
    ccx_installed = shutil.which('ccx')
    if not ccx_installed:
        print('Installing calculix (ccx)')
        command_line = "sudo apt-get install calculix-ccx"
        subprocess.check_call(command_line, shell=True)
    else:
        print('calculix (ccx) present')

def ubuntu_remove():
    """Removes programs on ubuntu, uses apt"""
    ccx_installed = shutil.which('ccx')
    if not ccx_installed:
        print('calculix (ccx) is not on your system')
    else:
        print('Removing calculix (ccx)')
        command_line = "sudo apt-get remove calculix-ccx"
        subprocess.check_call(command_line, shell=True)
    gmsh_installed = shutil.which('gmsh')
    if not gmsh_installed:
        print('gmsh is not on your system')
    else:
        print('Removing gmsh')
        command_line = "sudo apt-get remove gmsh"
        subprocess.check_call(command_line, shell=True)

def mac_add():
    """Adds programs on mac, uses brew"""
    brew_installed = shutil.which('brew')
    if not brew_installed:
        print('Installing brew')
        url = 'https://raw.githubusercontent.com/Homebrew/install/master/install'
        command_line = "/usr/bin/ruby -e \"$(curl -fsSL %s)\"" % url
        subprocess.check_call(command_line, shell=True)
    else:
        print('brew present')
    gmsh_installed = shutil.which('gmsh')
    if not gmsh_installed:
        print('Installing gmsh')
        folder_path = os.path.dirname(os.path.abspath(__file__))
        dmginstall_path = os.path.join(folder_path, 'dmginstall.sh')
        url = 'http://gmsh.info/bin/MacOSX/gmsh-3.0.5-MacOSX.dmg'
        command_line = '%s %s' % (dmginstall_path, url)
        print('command_line=%s' % command_line)
        subprocess.check_call(command_line, shell=True)
        gmsh_path = '/Applications/Gmsh.app/Contents/MacOS/gmsh'
        command_line = "ln -s %s /usr/local/bin/gmsh" % gmsh_path
        subprocess.check_call(command_line, shell=True)
    else:
        print('gmsh present')
    ccx_installed = shutil.which('ccx')
    if not ccx_installed:
        print('Installing calculix (ccx)')
        command_line = "brew install brewsci/science/calculix-ccx"
        subprocess.check_call(command_line, shell=True)
        ccx_path = find_brew_binary_location('calculix-ccx', 'ccx')
        if not ccx_path:
            raise Exception('Failed to find ccx binary')
        command_line = "ln -s %s /usr/local/bin/ccx" % ccx_path
        subprocess.check_call(command_line, shell=True)
    else:
        print('calculix (ccx) present')

def find_brew_binary_location(package_folder, search_string):
    """Finds the location of a binary installed by homebrew"""
    match_str = '/usr/local/Cellar/%s/**/*%s*' % (package_folder,
                                             search_string)
    paths = glob.glob(match_str, recursive=True)
    for path in paths:
        if os.access(path, os.X_OK):
            return path
    return None

def mac_remove():
    """Removes programs on mac, uses brew"""
    brew_installed = shutil.which('brew')
    if not brew_installed:
        print('Installing brew')
        url = 'https://raw.githubusercontent.com/Homebrew/install/master/install'
        command_line = "/usr/bin/ruby -e \"$(curl -fsSL %s)\"" % url
        subprocess.check_call(command_line, shell=True)
    else:
        print('brew present')
    ccx_installed = shutil.which('ccx')
    if not ccx_installed:
        print('calculix (ccx) is not on your system')
    else:
        print('Removing calculix (ccx)')
        command_line = "rm /usr/local/bin/ccx"
        subprocess.check_call(command_line, shell=True)
        command_line = "brew uninstall calculix-ccx"
        subprocess.check_call(command_line, shell=True)
    gmsh_installed = shutil.which('gmsh')
    if not gmsh_installed:
        print('gmsh is not on your system')
    else:
        print('Removing gmsh')
        command_line = "rm /usr/local/bin/gmsh"
        subprocess.check_call(command_line, shell=True)
        command_line = "rm -rf /Applications/Gmsh.app"
        subprocess.check_call(command_line, shell=True)


def windows_add(bitsize):
    """Adds programs on windows"""
    gmsh_installed = shutil.which('gmsh')
    if not gmsh_installed:
        print('Installing gmsh')
        win_add_from_url(bitsize, 'http://gmsh.info/bin/Windows/', 'gmsh')
    else:
        print('gmsh present')

    ccx_installed = shutil.which('ccx')
    if not ccx_installed:
        print('Installing calculix (ccx)')
        url = "https://sourceforge.net/projects/calculixforwin/files/03.2/"
        win_add_ccx(bitsize, url, "ccx")
    else:
        print('calculix (ccx) present')

def windows_remove(bitsize):
    """Removes programs on windows"""
    gmsh_installed = shutil.which('gmsh')
    if not gmsh_installed:
        print('gmsh is not on your system')
    else:
        print('Removing gmsh')
        env_path = os.getenv('VIRTUAL_ENV', sys.exec_prefix)
        scripts_folder = '%s\Scripts\\' % env_path
        remove_like(scripts_folder, 'gmsh')
    ccx_installed = shutil.which('ccx')
    if not ccx_installed:
        print('ccx is not on your system')
    else:
        print('Removing ccx')
        env_path = os.getenv('VIRTUAL_ENV', sys.exec_prefix)
        scripts_folder = '%s\Scripts\\' % env_path
        ccx_folder = '%sccx' % scripts_folder
        add_remove_dll_links(ccx_folder, scripts_folder, add=False)
        remove_like(scripts_folder, 'ccx')

def remove_like(search_path, name):
    """
    Searches for files or folders matching name in search_path and deletes them
    """
    match_str = '%s*%s*' % (search_path, name)
    paths = glob.glob(match_str)
    for path in paths:
        print('Removing %s' % path)
        if os.path.isfile(path):
            os.unlink(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

def win_add_from_url(bitsize, binaries_url, program_name):
    """Installs a program from an apache server file listing page"""
    # Needs the user agent header to exist for it to send back the content
    user_agent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) '
                  'Gecko/20100101 Firefox/56.0')
    headers = {'User-Agent': user_agent}

    zipfile_regex = '.*%s.*' % program_name
    # Windows 10 64 bit, gmsh version: Gmsh 3.0.7-git-35176e26 hangs
    zipfile_name = zipfile_by_bitsize(binaries_url, headers, zipfile_regex,
                                      bitsize)

    zipfile_folder_name = zipfile_name.split('.')[0]
    zipfile_url = binaries_url + zipfile_name
    print('Downloading %s from %s' % (program_name, zipfile_url))
    response = requests.get(zipfile_url, stream=True, headers=headers)
    with open(zipfile_name, 'wb') as out_file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                out_file.write(chunk)
    print('Unzipping %s' % program_name)
    zip_ref = zipfile.ZipFile(zipfile_name, 'r')
    zip_ref.extractall(None)
    zip_ref.close()
    print('Removing %s zipfile' % program_name)
    os.remove(zipfile_name)

    env_path = os.getenv('VIRTUAL_ENV', sys.exec_prefix)
    folder_to = '%s\Scripts\%s' % (env_path, zipfile_folder_name)
    exe_loc = '%s\%s.exe' % (folder_to, program_name)
    exe_link = '%s\Scripts\%s.exe' % (env_path, program_name)
    paths = [exe_link, folder_to]
    for path in  paths:
        if os.path.isfile(path):
            os.unlink(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
    command_line = "move %s %s" % (zipfile_folder_name, folder_to)
    print('Installing %s to %s' % (program_name, folder_to))
    subprocess.check_call(command_line, shell=True)
    os.link(exe_loc, exe_link)

def zipfile_by_bitsize(binaries_url, headers, zipfile_regex, bitsize):
    """Returns the url linking to the correct zipfile"""
    # need to add code here to peg us to a whitelisted version of ccx + gmsh
    # this is used by ccx and gmsh
    res = requests.get(binaries_url, headers=headers)
    html = res.text
    urls = re.findall(r'href=[\'"]?([^\'" >]+)', html)
    pattern = re.compile(zipfile_regex)
    urls = [url for url in urls if pattern.match(url)]
    urls = urls[-2:]
    url_choices = {32: urls[0], 64: urls[1]}
    if 'win32' in urls[1] or 'Windows32' in urls[1]:
        url_choices = {32: urls[1], 64: urls[0]}
    return url_choices[bitsize]

def href_from_link_text(url, headers, link_text):
    response = requests.get(url, headers=headers)
    html = response.text.replace("\"", "'")
    link_text_pos = html.find(link_text)
    if link_text_pos == -1:
        issue_url = ('https://github.com/spacether/pycalculix/issues/new?title='
                     'CCX%20zip%20download%20fails%20on%20windows&body=Please%2'
                     '0update%20the%20installer.py%20get_direct_url%20function.'
                     '%20It%20no%20longer%20works')
        raise ValueError('Unable to download file because there was not a link '
                         'with text=\'%s\' on the page at url=%s\nTo fix this, '
                         'please click the \'Submit new issue\' button '
                         'here:\n%s' % (link_text, url, issue_url))
    href_pos = html[:link_text_pos].rfind('href')
    first_char = html.find("'", href_pos)+1
    last_char = html.find("'", first_char)
    return html[first_char:last_char]

def get_direct_url(url, headers):
    """Gets the zip direct download link from the project download page"""
    direct_download_url = href_from_link_text(url,
                                              headers,
                                              'Problems Downloading')
    parsed_download_url = urlparse(direct_download_url)
    if parsed_download_url.scheme not in ['http', 'https']:
        # url is relative, and is missing the scheme and netloc
        parsed_parent_url = urlparse(url)
        parsed_download_url = ParseResult(parsed_parent_url.scheme,
                                          parsed_parent_url.netloc,
                                          parsed_download_url.path,
                                          parsed_download_url.params,
                                          parsed_download_url.query,
                                          parsed_download_url.fragment)
        direct_download_url = parsed_download_url.geturl()
    direct_download_url = href_from_link_text(direct_download_url,
                                              headers,
                                              'direct link')
    return direct_download_url

def win_add_ccx(bitsize, binaries_url, program_name):
    """Installs ccx on a windows computer"""
    # Needs the user agent header to exist for it to send back the content
    user_agent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) '
                  'Gecko/20100101 Firefox/56.0')
    headers = {'User-Agent': user_agent}

    zipfile_regex = '.+CL.+win.+zip/download$'
    zipfile_webpage_url = zipfile_by_bitsize(binaries_url, headers,
                                             zipfile_regex, bitsize)

    zipfile_name = zipfile_webpage_url.split('/')[-2]
    zipfile_url = get_direct_url(zipfile_webpage_url, headers)

    print('Downloading %s from %s' % (zipfile_name, zipfile_url))
    response = requests.get(zipfile_url, stream=True, headers=headers)
    with open(zipfile_name, 'wb') as out_file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                out_file.write(chunk)
    print('Unzipping %s' % program_name)
    zip_ref = zipfile.ZipFile(zipfile_name, 'r')
    zipfile_folder_name = zip_ref.namelist()[0].split('/')[0]
    zipfile_ccx_path = zipfile_folder_name + '/bin/ccx'
    for member in zip_ref.namelist():
        if zipfile_ccx_path in member:
            zip_ref.extract(member)
    zip_ref.close()
    print('Removing %s zipfile' % program_name)
    os.remove(zipfile_name)

    folder_from = '%s\\bin\\ccx' % zipfile_folder_name
    env_path = os.getenv('VIRTUAL_ENV', sys.exec_prefix)
    scripts_path = '%s\Scripts' % env_path
    folder_to = '%s\%s' % (scripts_path, program_name)

    binary_name = 'ccx212.exe'
    exe_loc = '%s\%s' % (folder_to, binary_name)
    exe_link = '%s\%s.exe' % (scripts_path, program_name)
    paths = [exe_link, folder_to]
    for path in  paths:
        if os.path.isfile(path):
            os.unlink(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

    print('Installing %s to %s' % (program_name, folder_to))
    copy_tree(folder_from, folder_to)
    shutil.rmtree(zipfile_folder_name)
    add_remove_dll_links(folder_to, scripts_path, add=True)
    os.link(exe_loc, exe_link)

def add_remove_dll_links(folder_dlls, folder_dll_links, add=True):
    """
    Finds all dlls in folder_from and adds hard links to them in folder_to
    Or removes the hard links if add=False
    """
    match_str = '%s\*.dll' % folder_dlls
    dll_paths = glob.glob(match_str)
    for dll_path in dll_paths:
        dll_name = dll_path.split('\\')[-1]
        dll_link_path = '%s\%s' % (folder_dll_links, dll_name)
        if add:
            os.link(dll_path, dll_link_path)
        elif os.path.isfile(dll_link_path):
            os.unlink(dll_link_path)
