'use client'
import {useState} from 'react'
import {BASE_URL} from '@/constants/url'
import {useKindeBrowserClient} from '@kinde-oss/kinde-auth-nextjs'
import {TokenTemplate} from '@/types/Tokens'

const useCreateToken = (data: TokenTemplate) => {
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)
    const {accessTokenEncoded} = useKindeBrowserClient()

    const submit = async () => {
        const headers = {
            'Authorization': `Bearer ${accessTokenEncoded}`,
            'Content-Type': 'application/json',
        }
        setIsLoading(true)
        setError(null)
        try {
            const response = await fetch(`${BASE_URL}/whatsapp-tokens`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(data),
            })
            setIsLoading(false)
            return await response.json()
        } catch (error: any) {
            setError(error)
            setIsLoading(false)
            throw error
        }
    }

    return {submit, isLoading, error}
}

export default useCreateToken
