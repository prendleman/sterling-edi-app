# Federated Group Branding Guide

Branding guidelines and logo usage for the EDI application.

## Logo Placement

### Application Branding

#### Dashboard Branding
- **Power BI Dashboards**: Add Federated Group logo to dashboard headers
- **Location**: Top-right or top-center of each dashboard page
- **Size**: Appropriate for dashboard layout
- **Format**: PNG with transparent background recommended

#### API Documentation
- **API Server**: Add logo to API documentation pages
- **Location**: Header section
- **Size**: Standard header size
- **Format**: PNG or SVG

#### Application Interface
- **CLI Output**: Optional logo in welcome messages
- **Reports**: Logo on report headers
- **Email Templates**: Logo in email signatures

### Documentation Branding

#### Document Headers
- **All Documentation**: Federated Group logo in document headers
- **Location**: Top of first page
- **Size**: Standard document header size
- **Format**: PNG or high-resolution for PDFs

#### Report Covers
- **Executive Reports**: Logo on report covers
- **Presentations**: Logo on title slides
- **Proposals**: Logo on proposal covers

## Logo Files

### Required Logo Files

Place logo files in `assets/branding/` directory:

```
assets/
└── branding/
    ├── logo.png              # Main logo (transparent background)
    ├── logo_white.png        # White version (for dark backgrounds)
    ├── logo_black.png        # Black version (for light backgrounds)
    ├── logo_icon.png         # Icon/favicon version
    └── logo_horizontal.png   # Horizontal layout version
```

### Logo Specifications

#### Main Logo
- **Format**: PNG with transparency
- **Minimum Size**: 200px width
- **Aspect Ratio**: Maintain original aspect ratio
- **Background**: Transparent

#### Icon Version
- **Format**: PNG
- **Size**: 64x64px or 128x128px
- **Usage**: Favicons, small icons

#### Horizontal Version
- **Format**: PNG
- **Usage**: Wide headers, banners
- **Aspect Ratio**: Wide format

## Brand Colors

### Primary Colors

If Federated Group has brand colors, configure in `config/branding.yaml`:

```yaml
branding:
  colors:
    primary: "#1B365D"      # Example: Navy blue
    secondary: "#C4962E"    # Example: Gold
    accent: "#4A9B4A"       # Example: Green
    text: "#333333"         # Dark gray
    background: "#FFFFFF"   # White
```

### Usage Guidelines

- **Primary Color**: Main brand color for headers, buttons
- **Secondary Color**: Accent color for highlights
- **Accent Color**: Call-to-action elements
- **Text Color**: Body text
- **Background**: Page backgrounds

## Typography

### Font Recommendations

If Federated Group has brand fonts:

```yaml
branding:
  fonts:
    heading: "Arial, sans-serif"      # Headings
    body: "Arial, sans-serif"         # Body text
    code: "Courier New, monospace"    # Code blocks
```

## Branding Configuration

### Configuration File

Create `config/branding.yaml`:

```yaml
# Federated Group Branding Configuration

branding:
  # Company Information
  company_name: "Federated Group"
  company_tagline: "Private Brand Sales and Marketing"
  
  # Logo Paths
  logos:
    main: "assets/branding/logo.png"
    white: "assets/branding/logo_white.png"
    black: "assets/branding/logo_black.png"
    icon: "assets/branding/logo_icon.png"
    horizontal: "assets/branding/logo_horizontal.png"
  
  # Brand Colors
  colors:
    primary: "#1B365D"
    secondary: "#C4962E"
    accent: "#4A9B4A"
    text: "#333333"
    background: "#FFFFFF"
  
  # Typography
  fonts:
    heading: "Arial, sans-serif"
    body: "Arial, sans-serif"
    code: "Courier New, monospace"
  
  # Contact Information
  contact:
    website: "https://www.federatedgroup.com"
    email: "info@federatedgroup.com"
    phone: ""
```

## Implementation

### Power BI Dashboard Branding

Update `src/powerbi_dashboard.py` and `src/powerbi_financial_dashboards.py` to include logo:

```python
# Add logo to dashboard
logo_visual = {
    "x": 1100, "y": 20, "w": 150, "h": 50,
    "type": "image",
    "image_url": "assets/branding/logo.png",
    "title": "Federated Group"
}
```

### API Server Branding

Update `src/api_server.py` to include branding in responses:

```python
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "EDI Processor API",
        "company": "Federated Group",
        "version": "2.0.0"
    }), 200
```

### Documentation Branding

Add logo to all markdown documentation headers:

```markdown
![Federated Group Logo](assets/branding/logo.png)

# Document Title
```

## Usage Guidelines

### Do's

✅ Use logo consistently across all materials
✅ Maintain aspect ratio
✅ Use appropriate size for context
✅ Use transparent background when possible
✅ Follow brand color guidelines

### Don'ts

❌ Don't distort or stretch logo
❌ Don't use low-resolution versions
❌ Don't modify logo colors
❌ Don't place logo on busy backgrounds
❌ Don't use logo smaller than minimum size

## File Structure

```
sterling_edi_app/
├── assets/
│   └── branding/
│       ├── logo.png
│       ├── logo_white.png
│       ├── logo_black.png
│       ├── logo_icon.png
│       └── logo_horizontal.png
├── config/
│   └── branding.yaml
└── docs/
    └── BRANDING_GUIDE.md
```

## Adding Your Logo

### Steps to Add Logo

1. **Obtain Logo Files**
   - Get logo files from marketing/branding team
   - Ensure high-resolution versions
   - Get multiple formats if available

2. **Create Assets Directory**
   ```bash
   mkdir -p assets/branding
   ```

3. **Place Logo Files**
   - Copy logo files to `assets/branding/` directory
   - Name files according to specifications

4. **Update Configuration**
   - Edit `config/branding.yaml`
   - Update logo paths if needed
   - Add brand colors if available

5. **Test Branding**
   - Verify logos appear correctly
   - Check all dashboards
   - Review documentation
   - Test API responses

## Branding Checklist

- [ ] Logo files placed in `assets/branding/`
- [ ] `config/branding.yaml` configured
- [ ] Power BI dashboards updated with logo
- [ ] API responses include branding
- [ ] Documentation includes logo
- [ ] Reports include branding
- [ ] Email templates include logo
- [ ] All branding tested and verified

## Support

For branding questions or logo files, contact:
- Marketing/Branding Team
- IT Department
- Design Team

