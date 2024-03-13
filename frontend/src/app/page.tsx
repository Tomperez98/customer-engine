'use client'

import Button from '@/components/Button'
import {RegisterLink, LoginLink} from '@kinde-oss/kinde-auth-nextjs/components'

const Login = () => {
    return (
        <main className='bg-gray-100-200 flex h-screen w-screen items-center justify-center p-8'>
            <section className='flex h-full w-full rounded-2xl bg-white shadow-md'>
                <div className='flex w-1/2 flex-col flex-wrap items-center justify-center px-12'>
                    <h1 className='text-6xl font-extrabold'>
                        <span className='text-2xl font-semibold'>
                            Bienvenido
                        </span>
                        <br />
                        Customer engine
                    </h1>
                </div>
                <div className='flex grow flex-col items-center justify-center gap-6'>
                    <LoginLink>
                        <Button
                            label='Iniciar sesión'
                            onClick={() => null}
                            size='xl'
                        />
                    </LoginLink>
                    <RegisterLink authUrlParams={{is_create_org: 'true'}}>
                        <Button
                            label='Registro'
                            onClick={() => null}
                            style='secondary'
                            size='xl'
                        />
                    </RegisterLink>
                </div>
            </section>
        </main>
    )
}

export default Login
