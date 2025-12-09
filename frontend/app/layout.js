import './globals.css'

export const metadata = {
  title: 'Yupoo Search Engine - FashionReps Trusted Sellers',
  description: 'Search 200+ FashionReps trusted sellers. Find clothing, shoes, bags, and accessories with real prices.',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
