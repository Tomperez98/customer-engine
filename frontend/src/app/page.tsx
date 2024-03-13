'use client'

import {RegisterLink, LoginLink} from '@kinde-oss/kinde-auth-nextjs/components'

const Login = () => {
    return (
        <main className='flex h-screen w-screen items-center justify-center bg-neutral-800 p-8'>
            <section className='flex h-full w-full   rounded-2xl bg-slate-200'>
                <div className='flex w-1/2 flex-col items-center justify-center'>
                    <h1>
                        <span>Bienvenido</span> Customer engine
                    </h1>
                </div>
                <div className='flex grow flex-col items-center justify-center'>
                    <RegisterLink authUrlParams={{is_create_org: 'true'}}>
                        Registro
                    </RegisterLink>
                    <LoginLink>Iniciar sesión</LoginLink>
                </div>
            </section>
        </main>
    )
}

export default Login
