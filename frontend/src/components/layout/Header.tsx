'use client'

import {LogoutLink, useKindeBrowserClient} from '@kinde-oss/kinde-auth-nextjs'

const Header = (): JSX.Element => {
    const {user} = useKindeBrowserClient()

    const userName = user
        ? `${user.given_name} 
    ${user.family_name?.[0]}`
        : 'Usuario'

    return (
        <header className='flex items-center justify-end gap-2 bg-white px-8 py-4 font-bold shadow-sm'>
            <p>{userName}</p>
            <LogoutLink>Cerrar Sesión</LogoutLink>
        </header>
    )
}

export default Header
