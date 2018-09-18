$envs = @(
    ("fps-in-file-&download", "sh /home/centos/run-fps-in-file-download.sh", '54.38.137.247'),
    ("fps-in-file-&process", "sh /home/centos/run-fps-in-file-process.sh", '54.38.137.183')
)
$envChoiceDesc = New-Object System.Collections.ObjectModel.Collection[System.Management.Automation.Host.ChoiceDescription]
for ($i = 0; $i -lt $envs.length; $i++) {
    $envChoiceDesc.Add((New-Object System.Management.Automation.Host.ChoiceDescription $envs[$i][0] ) ) 
}
$result = $Host.ui.PromptForChoice("RUN BACS scripts on SID", "Choose FPS script", $envChoiceDesc, 0)

$test = "''" + $($envs[$result][1]) + "''"
plink centos@$($envs[$result][2]) -i ovh-orwell-sid.ppk $test
Start-Sleep -s 7
