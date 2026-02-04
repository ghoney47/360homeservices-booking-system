import React from 'react'

const BookingLayout = ({ children, }: {children: React.ReactNode}) => {
  return (
    <html lang='en'>
        <body>
            <main> {children} </main>
        </body>

    </html>
  )
}

export default BookingLayout