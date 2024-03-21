import {useEffect, useState} from 'react'
import {BASE_URL} from '@/constants/url'
import {useKindeBrowserClient} from '@kinde-oss/kinde-auth-nextjs'
import {Token} from '@/types/Tokens'

type TokenResponse = {
    token: Token
}

const useGetToken = () => {
    const [data, setData] = useState<TokenResponse>()
    const [isLoading, setIsLoading] = useState<boolean>(false)
    const [errorCode, setErrorCode] = useState<number | null>(null)
    const {accessTokenEncoded} = useKindeBrowserClient()

    const fetchForms = async () => {
        if (!accessTokenEncoded) return
        const headers = {
            Authorization: `Bearer ${accessTokenEncoded}`,
        }
        setIsLoading(true)
        setErrorCode(null)

        try {
            const res = await fetch(`${BASE_URL}/whatsapp-tokens`, {
                headers: headers,
            })
            if (!res.ok) {
                setErrorCode(res.status)
                throw new Error(`HTTP error: ${res.status}`)
            }
            const resJson = await res.json()

            setData(resJson)
        } catch (error) {
            console.log(error)
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        if (accessTokenEncoded) {
            fetchForms()
        }
    }, [accessTokenEncoded])

    const refetch = () => {
        fetchForms()
    }

    return {data, isLoading, refetch, errorCode}
}

export default useGetToken
