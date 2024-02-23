import {ReactNode} from 'react'
import Header from './Header'

const Layout = ({children}: {children: ReactNode}): JSX.Element => {
    return (
        <div className='flex h-screen'>
            <div
                style={{
                    background:
                        'linear-gradient(112.1deg, rgb(32, 38, 57) 11.4%, rgb(63, 76, 119) 70.2%)',
                }}
                className='flex w-16 justify-center  p-8 text-lg font-bold text-white'>
                CE
            </div>
            <div className='flex max-h-full w-full flex-col overflow-hidden'>
                <Header />
                <main className='flex-grow overflow-y-auto p-8'>
                    {children}
                </main>
            </div>
        </div>
    )
}

export default Layout
