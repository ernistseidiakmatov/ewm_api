-- Users Table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    phone_number VARCHAR,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Reviews Table
CREATE TABLE user_reviews (
    review_id UUID PRIMARY KEY,
    reviewer_id UUID NOT NULL,
    reviewed_user_id UUID NOT NULL,
    review_comment TEXT NOT NULL,
    review_score INTEGER NOT NULL CHECK (review_score BETWEEN 1 and 5),
    review_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reviewer_id) REFERENCES users(user_id),
    FOREIGN KEY (reviewed_user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_user_reviews_reviewed_user_id ON user_reviews(reviewed_user_id);

ALTER TABLE user_reviews ADD CONSTRAINT unique_review 
UNIQUE (reviewer_id, reviewed_user_id);

-- Prevent Self-Review Function and Trigger
CREATE FUNCTION prevent_self_review() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.reviewer_id = NEW.reviewed_user_id THEN
        RAISE EXCEPTION 'Users cannot review themselves';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER no_self_reviews
BEFORE INSERT OR UPDATE ON user_reviews
FOR EACH ROW EXECUTE FUNCTION prevent_self_review();


-- Locations Table
CREATE TABLE locations (
    location_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    full_address TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX idx_locations_lat_long ON locations(latitude, longitude);

-- Restaurants Table
CREATE TABLE restaurants (
    restaurant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    contact_info JSONB NOT NULL,
    rating DECIMAL(3, 2) CHECK (rating >= 0 AND rating <= 5),
    location_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_location
        FOREIGN KEY (location_id)
        REFERENCES locations(location_id)
);

CREATE INDEX idx_restaurants_name ON restaurants(name);
CREATE INDEX idx_restaurants_location_id ON restaurants(location_id);


-- Events Table
CREATE TABLE events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_name VARCHAR(255) NOT NULL,
    event_description TEXT,
    event_date_time TIMESTAMP WITH TIME ZONE NOT NULL,
    registered_participants INTEGER NOT NULL DEFAULT 0,
    max_capacity INTEGER NOT NULL,
    event_status VARCHAR(20) NOT NULL DEFAULT 'upcoming',
    restaurant_id UUID NOT NULL,
    host_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_restaurant
        FOREIGN KEY (restaurant_id) 
        REFERENCES restaurants(restaurant_id),
    
    CONSTRAINT fk_host
        FOREIGN KEY (host_id) 
        REFERENCES users(user_id),
    
    CONSTRAINT check_capacity
        CHECK (registered_participants <= max_capacity),
    
    CONSTRAINT check_status
        CHECK (event_status IN ('upcoming', 'ongoing', 'completed', 'cancelled')),
    
    CONSTRAINT check_positive_capacity
        CHECK (max_capacity > 0)
);

-- Event Indexes
CREATE INDEX idx_events_restaurant_id ON events(restaurant_id);
CREATE INDEX idx_events_host_id ON events(host_id);
CREATE INDEX idx_events_event_date_time ON events(event_date_time);
CREATE INDEX idx_events_status ON events(event_status);
CREATE INDEX idx_events_capacity ON events(registered_participants, max_capacity);

-- Update Modified Column Function and Trigger
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER update_events_modtime
BEFORE UPDATE ON events
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();

-- Event Participants Table
CREATE TABLE event_participants (
    event_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'attendee',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (event_id, user_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_event_participants_user_id ON event_participants(user_id);

-- Register Participant Function
CREATE OR REPLACE FUNCTION register_participant(p_event_id UUID, p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    v_current_participants INTEGER;
    v_max_capacity INTEGER;
    v_host_id UUID;
    v_role VARCHAR(50);
BEGIN
    -- Get current number of participants, max capacity, and host_id
    SELECT registered_participants, max_capacity, host_id
    INTO v_current_participants, v_max_capacity, v_host_id
    FROM events 
    WHERE event_id = p_event_id;

    -- Determine the role
    IF p_user_id = v_host_id THEN
        v_role := 'host';
    ELSE
        v_role := 'attendee';
    END IF;

    -- Check if there's space available (for attendees)
    IF v_role = 'attendee' AND v_current_participants >= v_max_capacity THEN
        RETURN FALSE;
    END IF;

    -- Add participant
    INSERT INTO event_participants (event_id, user_id, role)
    VALUES (p_event_id, p_user_id, v_role)
    ON CONFLICT (event_id, user_id) DO NOTHING;

    -- Increment registered_participants (only for attendees)
    IF v_role = 'attendee' THEN
        UPDATE events 
        SET registered_participants = registered_participants + 1
        WHERE event_id = p_event_id;
    END IF;

    RETURN TRUE;
END;
$$ LANGUAGE 'plpgsql';

-- Register Host Trigger
CREATE OR REPLACE FUNCTION register_host_on_event_creation()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM register_participant(NEW.event_id, NEW.host_id);
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER register_host_trigger
AFTER INSERT ON events
FOR EACH ROW
EXECUTE FUNCTION register_host_on_event_creation();





