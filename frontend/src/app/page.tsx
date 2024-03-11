'use client'

import {RegisterLink, LoginLink} from '@kinde-oss/kinde-auth-nextjs/components'

const Login = () => {
    return (
        <main className='flex h-screen w-screen items-center justify-center'>
            <section className='flex flex-col items-center justify-center'>
                <h1>Welcome to Customer engine</h1>
                <RegisterLink authUrlParams={{is_create_org: 'true'}}>
                    Register
                </RegisterLink>
                <p>- or -</p>
                <LoginLink>Sign in</LoginLink>
            </section>
        </main>
    )
}

export default Login
