$d=Get-Disk -Number 1
if($d.BusType -ne 'USB' -or $d.FriendlyName -ne 'ASMT 2115' -or $d.IsBoot){ "ABORT wrong disk" | Out-File C:\evo-x3\records\usb-wipe.txt; exit 1 }
Clear-Disk -Number 1 -RemoveData -RemoveOEM -Confirm:$false
Initialize-Disk -Number 1 -PartitionStyle GPT
New-Partition -DiskNumber 1 -UseMaximumSize -DriveLetter F | Format-Volume -FileSystem NTFS -NewFileSystemLabel X3BACKUP -Confirm:$false
Get-Volume -DriveLetter F | Select DriveLetter,FileSystemLabel,FileSystem,Size,SizeRemaining | Out-File C:\evo-x3\records\usb-wipe.txt
