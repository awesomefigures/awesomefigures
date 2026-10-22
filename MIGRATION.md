# Migrating from contrastcolors to awesomefigures

The PyPI distribution and Python import package are now **awesomefigures**.
The recommended alias is `af`:

```python
import awesomefigures as af
af.set_style('elegante')
```

To migrate a previously installed editable development environment:

```bash
python -m pip uninstall -y contrastcolors
python -m pip install -e .
```

The previous import name `contrastcolors` is no longer installed by this repository. Previously generated notebook outputs and published demonstration PDFs may still contain the old branding until rebuilt. The GitHub repository remains `heri-espino/Colors` and GitHub Pages URLs are unchanged for now. No PyPI upload or repository rename is performed in this change.
