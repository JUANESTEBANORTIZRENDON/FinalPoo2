# PowerShell script to commit SonarQube configuration fix
# Run this script to commit and push the changes

Write-Host "Committing SonarQube configuration fix..." -ForegroundColor Green

# Add the modified files
git add sonar-project.properties
git add catalogos/templates/catalogos/impuestos_crear.html
git add catalogos/templates/catalogos/impuestos_editar.html
git add catalogos/templates/catalogos/metodos_pago_editar.html
git add templates/catalogos/metodos_pago_crear.html
git add SONARQUBE_FIX.md

# Show what will be committed
Write-Host "`nFiles to be committed:" -ForegroundColor Yellow
git status --short

# Commit with descriptive message
git commit -m "fix: Add SonarQube exclusion for Django template inheritance false positives

- Added Web:ItemTagNotWithinContainerTagCheck exclusion in sonar-project.properties
- This rule was flagging <li> tags in Django child templates as errors
- These tags are correctly rendered inside <ol> containers from parent templates
- This is standard Django template inheritance pattern and produces valid HTML
- Fixes false positive errors in impuestos_crear.html, impuestos_editar.html, 
  metodos_pago_editar.html, and metodos_pago_crear.html"

Write-Host "`nCommit created successfully!" -ForegroundColor Green
Write-Host "`nTo push to remote repository, run:" -ForegroundColor Yellow
Write-Host "git push" -ForegroundColor Cyan

# Optionally push automatically (uncomment the line below)
# git push
