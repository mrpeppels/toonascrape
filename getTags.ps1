Param(
  [string]$mode = "artist",
  [string]$rootfolder = "C:\Users\Alwin\Google Drive\music"
)

if(([appdomain]::currentdomain.getassemblies() | Where {$_ -match "taglib"}) -eq $null)
{
    [Reflection.Assembly]::LoadFrom(".\etc\taglib-sharp.dll") > null
}

$pshost = get-host
$pswindow = $pshost.ui.rawui
$newsize = $pswindow.windowsize
$newsize.height = 2
$newsize.width = 60
$pswindow.windowsize = $newsize


$artistList = New-Object System.Collections.ArrayList
$albumList = New-Object System.Collections.ArrayList


function printListToFile($list)
{
    
    del "./etc/local_lib_info.txt"
    " " | Out-File -Append -Encoding ascii -FilePath "./etc/local_lib_info.txt"
    foreach ($item in $list) 
    {
        if ($item.length -ne "" )
        {
            $item | Out-File -Append -Encoding ascii -FilePath "./etc/local_lib_info.txt"
        }
    }

}

Get-ChildItem -Recurse -Include *.mp3,*.wav,*.flac,*m4a $rootfolder | ForEach-Object {
    $songPath = $_.FullName
    $song = $_.Name
    
    $media = [TagLib.File]::Create($songPath)

    $songArtist = $media.Tag.AlbumArtists
    $songAlbum = $media.Tag.Album

    $artistList.Add($songArtist) > null
    $albumList.Add($songAlbum) > null
    
#    Write-Host "Title of " $song " is " $media.Tag.Title
#    Write-Host "Artist of " $song " is " 
#    Write-Host "Album of " $song " is " $media.Tag.Album

    if ($media)
    {
        try
        {
        Write-Host -NoNewline "Processing: " $song "                                                                                                                              `r"
        $media.Save()
        }
        catch [Exception]
        {
          echo $_.Exception.GetType().FullName, $_.Exception.Message
        }
    }
}


Switch ($Mode)
{
 "artist" { printListToFile($artistList) }
 "album" { printListToFile($albumList) }
}
