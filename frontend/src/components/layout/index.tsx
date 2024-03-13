import {ReactNode} from 'react'
import Header from './Header'
import Link from 'next/link'
import {useKindeBrowserClient} from '@kinde-oss/kinde-auth-nextjs'
import Sidebar from './Sidebar'

const Layout = ({children}: {children: ReactNode}): JSX.Element => {
    const {isAuthenticated} = useKindeBrowserClient()
    return (
        <>
            {isAuthenticated ? (
                <div className='flex h-screen'>
                    <Sidebar />
                    <div className='flex max-h-full w-full flex-col overflow-hidden'>
                        <Header />
                        <main className='flex-grow overflow-y-auto p-8'>
                            {children}
                        </main>
                    </div>
                </div>
            ) : (
                <div className='flex h-screen items-end justify-center'>no</div>
            )}
        </>
    )
}

export default Layout
