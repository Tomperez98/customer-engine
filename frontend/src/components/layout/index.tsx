import {ReactNode} from 'react'
import Header from './Header'
import Link from 'next/link'
import {LogoutLink, useKindeBrowserClient} from '@kinde-oss/kinde-auth-nextjs'

const Layout = ({children}: {children: ReactNode}): JSX.Element => {
    const {isAuthenticated} = useKindeBrowserClient()
    return (
        <>
            {isAuthenticated ? (
                <div className='flex h-screen'>
                    <div
                        style={{
                            background:
                                'linear-gradient(112.1deg, rgb(32, 38, 57) 11.4%, rgb(63, 76, 119) 70.2%)',
                        }}
                        className='flex w-16 flex-col items-center justify-start gap-2 p-8 text-lg font-bold text-white'>
                        <Link href='/dashboard'>CE</Link>
                        <Link href='/automatic-responses/create'>+</Link>
                    </div>
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
