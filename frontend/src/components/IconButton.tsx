interface IconButtonProps {
    Icon: any
    onClick: () => void
}

const IconButton = ({Icon, onClick}: IconButtonProps) => {
    return (
        <button onClick={onClick}>
            <Icon />
        </button>
    )
}

export default IconButton
