import './globals.css';

export const metadata = {
  title: 'Product Launch Studio | AI-Powered Marketplace Builder',
  description:
    'Upload your product images, enter details, and instantly get AI-generated listings, packaging designs, pricing, and compliance insights for Amazon, Flipkart, and Meesho.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <header className="site-header">
          <div className="container">
            <div className="inner">
              <div className="logo-mark">🚀</div>
              <div>
                <h1 className="gradient-text">Product Launch Studio</h1>
                <p className="tagline">AI-Powered Marketplace Builder · Amazon · Flipkart · Meesho</p>
              </div>
            </div>
          </div>
        </header>
        <main style={{ padding: '40px 0 80px' }}>
          {children}
        </main>
      </body>
    </html>
  );
}
