'use client'

import {LogoutLink, useKindeBrowserClient} from '@kinde-oss/kinde-auth-nextjs'
import Button from '../Button'

const Header = (): JSX.Element => {
    const {user, accessTokenEncoded} = useKindeBrowserClient()

    const userName = user
        ? `${user.given_name} 
    ${user.family_name?.[0]}`
        : 'Usuario'

    return (
        <header className='flex items-center justify-end gap-4 bg-white px-8 py-4 shadow-sm'>
            <p className='text-md font-bold text-neutral-800'>{userName}</p>
            <LogoutLink>
                <Button size='sm' onClick={() => null} label='Cerrar Sesión' />
            </LogoutLink>
        </header>
    )
}

export default Header
