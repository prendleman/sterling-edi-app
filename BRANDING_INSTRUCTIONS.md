# Adding Federated Group Branding

Instructions for adding Federated Group logo and branding to the application.

## Quick Start

1. **Obtain Logo Files**
   - Contact Federated Group marketing/branding team
   - Request logo files in PNG format with transparent background
   - Get multiple versions: main, white, black, icon, horizontal

2. **Place Logo Files**
   - Create directory: `assets/branding/`
   - Copy logo files to this directory
   - Name files as specified in `assets/branding/README.md`

3. **Update Brand Colors** (Optional)
   - Edit `config/branding.yaml`
   - Update colors with Federated Group brand colors
   - Update contact information

4. **Verify Branding**
   - Generate Power BI dashboards (logos will appear automatically)
   - Check API responses (company name included)
   - Review documentation (add logos manually if desired)

## Logo File Requirements

### Required Files

Place these files in `assets/branding/`:

- `logo.png` - Main logo (transparent background, 200px+ width)
- `logo_white.png` - White version for dark backgrounds
- `logo_black.png` - Black version for light backgrounds  
- `logo_icon.png` - Icon version (64x64 or 128x128px)
- `logo_horizontal.png` - Horizontal layout for banners

### File Specifications

- **Format**: PNG with transparency
- **Resolution**: High resolution (300 DPI for print)
- **Background**: Transparent (no white background)
- **Quality**: Clear and crisp at all sizes

## Brand Colors

If you have Federated Group brand colors, update `config/branding.yaml`:

```yaml
colors:
  primary: "#YOUR_PRIMARY_COLOR"
  secondary: "#YOUR_SECONDARY_COLOR"
  accent: "#YOUR_ACCENT_COLOR"
```

## Where Branding Appears

Once logo files are added:

✅ **Power BI Dashboards** - Logo automatically added to dashboards
✅ **API Responses** - Company name included in API responses
✅ **Documentation** - Can be added to document headers
✅ **Reports** - Logo can be added to generated reports

## Testing

After adding logos:

1. Generate a dashboard: `python main.py dashboard`
2. Check API: `curl http://localhost:5000/health`
3. Verify logo appears in dashboard
4. Check company name in API response

## Support

For logo files or branding questions:
- Contact Federated Group Marketing/Branding Team
- See `docs/BRANDING_GUIDE.md` for detailed guidelines

