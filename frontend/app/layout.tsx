// Import types for metadata configuration from Next.js
import type { Metadata } from 'next';

// Import Toaster component from sonner for toast notifications
import { Toaster } from 'sonner';

// Import custom ThemeProvider for managing dark/light themes
import { ThemeProvider } from '@/components/theme-provider';

// Import global CSS styles
import './globals.css';

// Metadata configuration for the entire application
export const metadata: Metadata = {
  // Base URL for the application (used for canonical URLs and open graph tags)
  metadataBase: new URL('https://recall.space'),
  
  // Default title of the application
  title: 'Lisa AI',
  
  // Description for SEO and sharing
  description: 'Lisa, intelligent material planner by Recall Space',
};

// Viewport configuration to prevent auto-zoom on mobile devices
export const viewport = {
  maximumScale: 1, // Disables automatic zooming on mobile Safari
};

// Define color values for light and dark themes
const LIGHT_THEME_COLOR = 'hsl(0 0% 100%)';
const DARK_THEME_COLOR = 'hsl(240deg 10% 3.92%)';

// JavaScript script to dynamically update theme-color meta tag
// This ensures the mobile browser's status bar matches the current theme
const THEME_COLOR_SCRIPT = `\
(function() {
  // Get the root HTML element
  var html = document.documentElement;
  
  // Find or create theme-color meta tag
  var meta = document.querySelector('meta[name="theme-color"]');
  if (!meta) {
    meta = document.createElement('meta');
    meta.setAttribute('name', 'theme-color');
    document.head.appendChild(meta);
  }
  
  // Function to update theme-color based on dark/light mode
  function updateThemeColor() {
    var isDark = html.classList.contains('dark');
    meta.setAttribute('content', isDark ? '${DARK_THEME_COLOR}' : '${LIGHT_THEME_COLOR}');
  }
  
  // Observe changes to HTML class to detect theme switches
  var observer = new MutationObserver(updateThemeColor);
  observer.observe(html, { attributes: true, attributeFilter: ['class'] });
  
  // Initial theme color setup
  updateThemeColor();
})();`;

// Root layout component for the entire application
export default async function RootLayout({
  children, // Child components to be rendered inside this layout
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    // HTML root element with language set to English
    <html
      lang="en"
      // Suppress hydration warning due to theme class injection
      // This prevents React warning about class differences between server and client
      suppressHydrationWarning
    >
      <head>
        {/* Inject script to dynamically update theme-color meta tag */}
        <script
          dangerouslySetInnerHTML={{
            __html: THEME_COLOR_SCRIPT,
          }}
        />
      </head>
      <body className="antialiased">
        {/* Theme Provider to manage dark/light mode */}
        <ThemeProvider
          attribute="class" // Use class to toggle themes
          defaultTheme="system" // Default to system preference
          enableSystem // Allow system theme detection
          disableTransitionOnChange // Prevent animation when switching themes
        >
          {/* Toast notification component positioned at top center */}
          <Toaster position="top-center" />
          
          {/* Render child components */}
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}